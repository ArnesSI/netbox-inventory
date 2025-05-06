from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from netbox.models import NetBoxModel
from netbox.models.features import ContactsMixin

from ..choices import BOMStatusChoices, PurchaseStatusChoices


class Supplier(NetBoxModel, ContactsMixin):
    """
    Supplier is a legal entity that sold some assets that we keep track of.
    This can be the same entity as Manufacturer or a separate one. However
    netbox_inventory keeps track of Suppliers separate from Manufacturers.
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

    clone_fields = ["description", "comments"]

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_inventory:supplier", args=[self.pk])


class BOM(NetBoxModel, ContactsMixin):
    """
    Represents a set of Assets with the consideration of Purchase.
    """

    name = models.CharField(max_length=100)
    status = models.CharField(
        max_length=30,
        choices=BOMStatusChoices,
        help_text="Status of BOM",
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )
    comments = models.TextField(
        blank=True,
    )

    clone_fields = ["status", "description", "comments"]

    class Meta:
        ordering = ["name"]
        verbose_name = "BOM"
        verbose_name_plural = "BOMs"
        unique_together = (("name"),)

    def get_status_color(self):
        return BOMStatusChoices.colors.get(self.status)

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse('plugins:netbox_inventory:bom', args=[self.pk])


class Purchase(NetBoxModel):
    """
    Represents a purchase of a set of Assets from a Supplier.
    """

    name = models.CharField(max_length=100)
    supplier = models.ForeignKey(
        help_text="Legal entity this purchase was made at",
        to="netbox_inventory.Supplier",
        on_delete=models.PROTECT,
        related_name="purchases",
        blank=False,
        null=False,
    )
    boms = models.ManyToManyField(
        help_text="BOMs that this purchase is part of",
        to="netbox_inventory.BOM",
        related_name="purchases",
        blank=True,
        verbose_name='BOMs',
    )
    status = models.CharField(
        max_length=30,
        choices=PurchaseStatusChoices,
        help_text="Status of purchase",
    )
    date = models.DateField(
        help_text="Date when this purchase was made",
        blank=True,
        null=True,
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )
    comments = models.TextField(
        blank=True,
    )

    clone_fields = ["supplier", "boms", "date", "status", "description", "comments"]

    class Meta:
        ordering = ["supplier", "name"]
        unique_together = (("supplier", "name"),)

    def get_status_color(self):
        return PurchaseStatusChoices.colors.get(self.status)

    def __str__(self):
        return f"{self.supplier} {self.name}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_inventory:purchase", args=[self.pk])


class Delivery(NetBoxModel):
    """
    Delivery is a stage in Purchase. Purchase can have multiple deliveries.
    In each Delivery one or more Assets were delivered.
    """

    name = models.CharField(max_length=100)
    purchases = models.ManyToManyField(
        help_text='Purchases that this delivery is part of',
        to='netbox_inventory.Purchase',
        related_name='orders',
        blank=False,
    )
    date = models.DateField(
        help_text="Date when this delivery was made",
        blank=True,
        null=True,
    )
    receiving_contact = models.ForeignKey(
        help_text="Contact that accepted this delivery",
        to="tenancy.Contact",
        on_delete=models.PROTECT,
        related_name="deliveries",
        blank=True,
        null=True,
    )
    delivery_location = models.ForeignKey(
        help_text='The location where this delivery is to be received',
        to='dcim.Location',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True,
        verbose_name='Delivery Location',
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )
    comments = models.TextField(
        blank=True,
    )

    clone_fields = [
        'purchases',
        'date',
        'receiving_contact',
        'delivery_location',
        'description',
        'comments'
    ]

    @property
    def delivery_site(self):
        if self.delivery_location:
            return self.delivery_location.site

    def clean(self):
        super().clean()
        if self.pk and self.purchases.count() == 0:
            raise ValidationError('A delivery must have at least one purchase.')

    class Meta:
        ordering = ['name']
        unique_together = (('name'),)
        verbose_name = 'delivery'
        verbose_name_plural = 'deliveries'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_inventory:delivery", args=[self.pk])
