from django.db import models
from django.forms import ValidationError
from django.urls import reverse

from netbox.models import NetBoxModel
from netbox.models.features import ContactsMixin

from ..choices import TransferStatusChoices
from ..models import Asset


class Courier(NetBoxModel, ContactsMixin):
    """
    Courier is a legal entity that handles some assets during a transfer.
    This can be the same entity as Supplier or a separate one. However
    netbox_inventory keeps track of Couriers separate from Suppliers.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )
    comments = models.TextField(
        blank=True,
    )

    clone_fields = ['description', 'comments']

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_inventory:courier', args=[self.pk])
    

class Transfer(NetBoxModel):
    """
    A Transfer represents a series of Assets that have been delivered between onsite
    locations by a Courier.
    """

    #
    # General
    #
    name = models.CharField(
        help_text='Can be used to quickly identify a particular transfer',
        max_length=128,
        blank=True,
        null=False,
        default='',
    )
    courier = models.ForeignKey(
        help_text='Courier that is handling this transfer',
        to='netbox_inventory.Courier',
        on_delete=models.PROTECT,
        related_name='transfers',
        blank=True,
        null=True,
    )
    shipping_number = models.CharField(
        help_text='Shipping number assigned to this transfer',
        max_length=60,
        blank=True,
        null=True,
        verbose_name='Shipping Number',
        default=None,
    )
    instructions = models.TextField(
        help_text='Delivery instructions for the courier',
        blank=True,
        verbose_name='Delivery Instructions',
    )
    status = models.CharField(
        max_length=30,
        choices=TransferStatusChoices,
        help_text='Transfer lifecycle status',
    )

    #
    # Transfer
    #
    sender = models.ForeignKey(
        help_text='Contact that is sending this transfer',
        to='tenancy.Contact',
        on_delete=models.PROTECT,
        related_name='sent_transfers',
        blank=False,
        null=False,
    )
    recipient = models.ForeignKey(
        help_text='Contact that is receiving this transfer',
        to='tenancy.Contact',
        on_delete=models.PROTECT,
        related_name='received_transfers',
        blank=False,
        null=False,
    )
    site = models.ForeignKey(
        help_text='Site where this transfer is to be delivered',
        to='dcim.Site',
        on_delete=models.PROTECT,
        related_name='transfers',
        blank=False,
        null=False,
    )
    location = models.ForeignKey(
        help_text='On-site location where this transfer is to be delivered',
        to='dcim.Location',
        on_delete=models.PROTECT,
        related_name='transfers',
        blank=True,
        null=True,
    )
    pickup_date = models.DateField(
        help_text='Date the courier picked up the transfer from sender',
        blank=True,
        null=True,
        verbose_name='Pickup Date',
    )
    received_date = models.DateField(
        help_text='Date the courier delivered the transfer to recipient',
        blank=True,
        null=True,
        verbose_name='Received Date',
    )
    comments = models.TextField(
        blank=True,
    )

    clone_fields = [
        'name',
        'instructions',
        'status',
        'sender',
        'recipient',
        'site',
        'location',
        'pickup_date',
        'received_date',
        'comments',
    ]

    def clean(self):
        self.validate_dates()
        return super().clean()
    
    def validate_dates(self):
        """
        Ensure that the received_date is after the pickup_date.
        """
        if self.pickup_date and self.received_date:
            if self.received_date < self.pickup_date:
                raise ValidationError({
                    'received_date': 'Received date must be after pickup date.',
                })

    def get_assets(self):
        """
        Return all assets that are part of this transfer.
        """
        return Asset.objects.filter(transfer_id=self.pk)

    def get_absolute_url(self):
        return reverse('plugins:netbox_inventory:transfer', args=[self.pk])

    def get_status_color(self):
        return TransferStatusChoices.colors.get(self.status)

    def __str__(self):
        if self.name:
            return self.name
        if self.shipping_number:
            return f'{self.shipping_number} (id:{self.id})'
        else:
            return f'(id:{self.id})'

    class Meta:
        ordering = (
            'sender',
            'pickup_date',
        )
        constraints = (
            models.UniqueConstraint(
                fields=('shipping_number',),
                name='unique_shipping_number',
                violation_error_message='Transfer with this Shipping Number already exists.',
            ),
        )