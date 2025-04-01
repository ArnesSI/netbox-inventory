from django.core.exceptions import FieldError, ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from core.models import ObjectChange, ObjectType
from netbox.models.features import (
    ChangeLoggingMixin,
    CloningMixin,
    EventRulesMixin,
)
from utilities.query import dict_to_filter_params
from utilities.querysets import RestrictedQuerySet

from ..constants import AUDITFLOW_OBJECT_TYPE_CHOICES
from .mixins import NamedModel

__all__ = (
    'AuditFlow',
    'AuditFlowPage',
    'AuditFlowPageAssignment',
)


class BaseFlow(NamedModel):
    """
    A `BaseFlow` provides the foundation for all audit flow models and provides the
    logic to bind a model instance to a specific set of objects.
    """

    object_type = models.ForeignKey(
        ObjectType,
        related_name='+',
        on_delete=models.PROTECT,
    )
    object_filter = models.JSONField(
        blank=True,
        null=True,
    )

    clone_fields = (
        'object_type',
        'object_filter',
    )

    class Meta(NamedModel.Meta):
        abstract = True

    def clean(self) -> None:
        super().clean()

        if self.object_filter:
            if type(self.object_filter) is not dict:
                raise ValidationError(
                    {
                        'object_filter': _(
                            'Filter must be defined as a dictionary mapping attributes '
                            'to values.'
                        )
                    }
                )

            # Validate the object_filter by retrieving the related object query set and
            # thus resolving the filter logic.
            try:
                self.get_objects()
            except FieldError as e:
                model = self.object_type.model_class()
                raise ValidationError(
                    {
                        'object_filter': _(
                            'Invalid filter for {model}: {error}'
                        ).format(model=model, error=e)
                    }
                ) from e

    def get_objects(self) -> models.QuerySet:
        """
        Get related objects.

        This method returns a queryset for `object_type` matching the defined
        `object_filter`.


        :returns: `QuerySet` to access applicable objects.
        """
        filter_params = dict_to_filter_params(self.object_filter or {})
        return self.object_type.model_class().objects.filter(**filter_params)


class AuditFlowPage(BaseFlow):
    """
    An `AuditFlowPage' defines a specific page in an `AuditFlow`. It is used to display
    a specific type of object to be audited.
    """

    pass


class AuditFlow(BaseFlow):
    """
    An `AuditFlow` defines a self-contained sequence of actions within the inventory
    audit process, meaning it groups all `AuditFlowPage` objects presented to the user.
    It is associated with a specific NetBox object type (e.g. `Site`, `Location` or
    `Rack`), from which the audit workflow can be initiated.
    """

    # Restrict inherited object_type to those object types that represent physical
    # locations.
    object_type = models.ForeignKey(
        ObjectType,
        related_name='+',
        on_delete=models.PROTECT,
        limit_choices_to=AUDITFLOW_OBJECT_TYPE_CHOICES,
    )

    enabled = models.BooleanField(
        verbose_name=_('enabled'),
        default=True,
    )
    pages = models.ManyToManyField(
        AuditFlowPage,
        through='AuditFlowPageAssignment',
        related_name='assigned_flows',
    )

    clone_fields = (
        'object_type',
        'object_filter',
        'enabled',
    )


class AuditFlowPageAssignment(
    ChangeLoggingMixin,
    CloningMixin,
    EventRulesMixin,
):
    """
    Mapping between `AuditFlow` and `AuditFlowPage` to add additional metadata.
    """

    flow = models.ForeignKey(
        AuditFlow,
        related_name='+',
        on_delete=models.CASCADE,
    )
    page = models.ForeignKey(
        AuditFlowPage,
        related_name='+',
        on_delete=models.PROTECT,
    )
    weight = models.PositiveSmallIntegerField(
        verbose_name=_('display weight'),
        default=100,
        help_text=_('Assignments with higher weights appear later in an audit flow.'),
    )

    objects = RestrictedQuerySet.as_manager()

    clone_fields = (
        'flow',
        'weight',
    )

    class Meta:
        ordering = ('weight',)
        constraints = (
            models.UniqueConstraint(
                fields=['flow', 'page'],
                name='%(app_label)s_%(class)s_unique_flow_page',
            ),
        )

    def __str__(self) -> str:
        return str(f'{self.flow} -> {self.page}')

    def get_absolute_url(self) -> str:
        return reverse('plugins:netbox_inventory:auditflowpage', args=[self.page.pk])

    def to_objectchange(self, action) -> ObjectChange:
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.flow
        return objectchange
