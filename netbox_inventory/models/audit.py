from django.core.exceptions import FieldError, ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from core.models import ObjectChange, ObjectType
from dcim.models import Location, Rack, Site
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
        related_name='assigned_pages',
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

    def clean(self) -> None:
        super().clean()

        # Validate that a page can actually be used for the specific flow by verifying
        # that a filter lookup can be generated.
        try:
            self._get_filter_lookup()
        except FieldError as e:
            raise ValidationError(
                {'page': _('Cannot use page for this flow: {error}').format(error=e)}
            ) from e

    def __str__(self) -> str:
        return str(f'{self.flow} -> {self.page}')

    def get_absolute_url(self) -> str:
        return reverse('plugins:netbox_inventory:auditflowpage', args=[self.page.pk])

    def to_objectchange(self, action) -> ObjectChange:
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.flow
        return objectchange

    @staticmethod
    def _get_lookup_paths(model: models.Model) -> list[tuple[models.Model, str | None]]:
        """
        Get a list of location lookup paths for `model`.

        A model is bound to a specific type of location, e.g. a `Location`. However, an
        `AuditFlow` might deal with an `object_type` in a higher hierarchy level. This
        method will generate a list of possible relationships between these two objects,
        even if there is no direct relationship.

        For example, if objects are to be filtered by `Site` and there is no direct
        relationship but only a `rack' field, objects can also be filtered by the `Site`
        field of the `Rack`.


        :param model: Model class used in `AuditFlow`.

        :returns: A tuple of the related model and its required lookup suffix. The list
            is returned from the most specific to the least specific field.
        """
        paths = [(model, None)]
        if model == Location:
            paths.append((Rack, 'location'))
        elif model == Site:
            paths.extend(
                [
                    (Location, 'site'),
                    (Rack, 'site'),
                ]
            )

        return paths

    def _get_filter_lookup(self) -> str:
        """
        Get the field lookup needed to filter page objects in an `AuditFlow`.
        """
        flow_model = self.flow.object_type.model_class()
        page_model = self.page.object_type.model_class()

        lookup_paths = self._get_lookup_paths(flow_model)
        related_models = {model for model, _ in lookup_paths}

        # Get all applicable ForeignKey fields of the page object type that map directly
        # or indirectly to the flow object type.
        related_fields = {
            field.related_model: field.name
            for field in page_model._meta.fields
            if (
                isinstance(field, models.ForeignKey)
                and field.related_model in related_models
            )
        }

        # Iterate over possible lookup paths. Return the first applicable path with the
        # highest precedence.
        for model, suffix in lookup_paths:
            lookup = related_fields.get(model)
            if lookup:
                if suffix:
                    lookup += f'__{suffix}'
                return lookup

        raise FieldError(f'No relation between {page_model} and {flow_model}')

    def get_objects(self, flow_start_object: models.Model) -> models.QuerySet:
        """
        Get audit objects for `flow_start_object`.

        This method filters the `AuditFlowPage` objects restricted to the `AuditFlow`
        location specified in `flow_start_object`.


        :param flow_start_object: Object used to start the `AuditFlow`, e.g. a `Site`.
        """
        filter_name = self._get_filter_lookup()
        return self.page.get_objects().filter(**{filter_name: flow_start_object})
