from django.db import models

from netbox.models.features import ContactsMixin

from ..choices import PurchaseStatusChoices
from .mixins import NamedModel


class Supplier(NamedModel, ContactsMixin):
    """
    Supplier is a legal entity that sold some assets that we keep track of.
    This can be the same entity as Manufacturer or a separate one. However
    netbox_inventory keeps track of Suppliers separate from Manufacturers.
    """

    slug = models.SlugField(
        max_length=100,
        unique=True,
    )

    clone_fields = ['description', 'comments']


class Purchase(NamedModel):
    """
    Represents a purchase of a set of Assets from a Supplier.
    """

    name = models.CharField(max_length=100)
    supplier = models.ForeignKey(
        help_text='Legal entity this purchase was made at',
        to='netbox_inventory.Supplier',
        on_delete=models.PROTECT,
        related_name='purchases',
        blank=False,
        null=False,
    )
    status = models.CharField(
        max_length=30,
        choices=PurchaseStatusChoices,
        help_text='Status of purchase',
    )
    date = models.DateField(
        help_text='Date when this purchase was made',
        blank=True,
        null=True,
    )

    clone_fields = ['supplier', 'date', 'status', 'description', 'comments']

    class Meta:
        ordering = ['supplier', 'name']
        unique_together = (('supplier', 'name'),)

    def get_status_color(self):
        return PurchaseStatusChoices.colors.get(self.status)

    def __str__(self):
        return f'{self.supplier} {self.name}'


class Delivery(NamedModel):
    """
    Delivery is a stage in Purchase. Purchase can have multiple deliveries.
    In each Delivery one or more Assets were delivered.
    """

    name = models.CharField(max_length=100)
    purchase = models.ForeignKey(
        help_text='Purchase that this delivery is part of',
        to='netbox_inventory.Purchase',
        on_delete=models.PROTECT,
        related_name='orders',
        blank=False,
        null=False,
    )
    date = models.DateField(
        help_text='Date when this delivery was made',
        blank=True,
        null=True,
    )
    receiving_contact = models.ForeignKey(
        help_text='Contact that accepted this delivery',
        to='tenancy.Contact',
        on_delete=models.PROTECT,
        related_name='deliveries',
        blank=True,
        null=True,
    )

    clone_fields = ['purchase', 'date', 'receiving_contact', 'description', 'comments']

    class Meta:
        ordering = ['purchase', 'name']
        unique_together = (('purchase', 'name'),)
        verbose_name = 'delivery'
        verbose_name_plural = 'deliveries'

    def __str__(self):
        return f'{self.purchase} {self.name}'
