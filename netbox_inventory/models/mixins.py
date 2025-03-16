from django.db import models
from django.utils.translation import gettext_lazy as _

from netbox.models import NetBoxModel


class NamedModel(NetBoxModel):
    """
    Named models represent something that can be identified by its name. An additional
    description and comments can be set.
    """

    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True,
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True,
    )
    comments = models.TextField(
        verbose_name=_('comments'),
        blank=True,
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name
