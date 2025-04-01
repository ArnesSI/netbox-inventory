from django.db import models
from django.urls import reverse

from netbox.models import NetBoxModel
from netbox.models.features import ContactsMixin


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