from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError, ValidationError
from django.db import models
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import ObjectChange, ObjectType
from dcim.models import Location, Rack, Site
from netbox.models import NestedGroupModel
from netbox.models.features import (
    ChangeLoggingMixin,
    CloningMixin,
    CustomValidationMixin,
    EventRulesMixin,
    ExportTemplatesMixin,
)
from utilities.query import dict_to_filter_params
from utilities.querysets import RestrictedQuerySet
from utilities.views import get_viewname

from ..constants import AUDITFLOW_OBJECT_TYPE_CHOICES
from .mixins import NamedModel

__all__ = (
    'AuditFlow',
    'AuditFlowPage',
    'AuditFlowPageAssignment',
    'AuditTrail',
    'AuditTrailSource',
)


LOOKUP_PATHS = list[tuple[type[models.Model], str | None]]


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

    class Meta(BaseFlow.Meta):
        verbose_name = _('audit flow page')
        verbose_name_plural = _('audit flow pages')

    def clean(self):
        super().clean()

        # Validate that the object_type is usable when running the audit by verifying
        # that a list view is available for its model class.
        try:
            model = self.object_type.model_class()
            reverse(get_viewname(model, 'list'))
        except NoReverseMatch as e:
            raise ValidationError(
                {
                    'object_type': _(
                        'Object type not supported: No list view for {model}'
                    ).format(model=model)
                }
            ) from e


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

    class Meta(BaseFlow.Meta):
        verbose_name = _('audit flow')
        verbose_name_plural = _('audit flows')


class AuditFlowPageAssignment(
    ChangeLoggingMixin,
    CloningMixin,
    EventRulesMixin,
    models.Model,
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
        verbose_name = _('audit flow page assignment')
        verbose_name_plural = _('audit flow page assignments')

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
    def _get_lookup_paths(model: type[models.Model]) -> LOOKUP_PATHS:
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
        paths: LOOKUP_PATHS = [(model, None)]
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

    def get_objects(
        self,
        start_object: models.Model | NestedGroupModel,
    ) -> models.QuerySet:
        """
        Get audit objects for `start_object`.

        This method filters the `AuditFlowPage` objects restricted to the `AuditFlow`
        location specified in `start_object`.


        :param start_object: Object used to start the `AuditFlow`, e.g. a `Site`.
        """
        filter_name = self._get_filter_lookup()

        # If the start object supports nesting, child locations are also searched to
        # allow easy auditing even if a specific location is subdivided into
        # sub-locations.
        if isinstance(start_object, NestedGroupModel):
            filter_name += '__in'
            start_object = start_object.get_descendants(include_self=True)

        return self.page.get_objects().filter(**{filter_name: start_object})


class AuditTrailSource(NamedModel):
    """
    An `AuditTrailSource` defines the source of an `AuditTrail`. This is useful when
    `AuditTrail` should be imported from other systems such as monitoring or automated
    inventory tools.
    """

    slug = models.SlugField(
        max_length=100,
        unique=True,
    )

    class Meta(NamedModel.Meta):
        verbose_name = _('audit trail source')
        verbose_name_plural = _('audit trail sources')


class AuditTrail(
    ChangeLoggingMixin,
    CustomValidationMixin,
    ExportTemplatesMixin,
    EventRulesMixin,
    models.Model,
):
    """
    An `AuditTrail` marks a specific object to be seen at a specific timestamp, e.g.
    when running an audit flow.
    """

    object_type = models.ForeignKey(
        to=ContentType,
        related_name='+',
        on_delete=models.PROTECT,
    )
    object_id = models.PositiveBigIntegerField()
    object = GenericForeignKey(
        ct_field='object_type',
        fk_field='object_id',
    )
    source = models.ForeignKey(
        AuditTrailSource,
        related_name='audit_trails',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    # Add a reverse relationship for object changes to display the auditor user in the
    # AuditTrailTable. Reusing the logic of the ObjectChange model and
    # ChangeLoggingMixin reduces the logic of this model because the request-response
    # cycle doesn't need to maintain who actually created the object.
    #
    # NOTE: A known limitation of this code is that related ObjectChange objects will be
    #       deleted if the audit trail itself is deleted. This is because a
    #       GenericRelation enforces a CASCADE deletion, which, according to Django's
    #       documentation, cannot be changed. However, using a GenericRelation greatly
    #       simplifies the code compared to using nested queries, especially for
    #       prefetching.
    object_changes = GenericRelation(
        ObjectChange,
        content_type_field='changed_object_type',
        object_id_field='changed_object_id',
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = (
            '-created',
            'object_type',
        )
        indexes = (models.Index(fields=('object_type', 'object_id')),)
        verbose_name = _('audit trail')
        verbose_name_plural = _('audit trails')

    def __str__(self) -> str:
        created = timezone.localtime(self.created)
        return (
            f'{created.date().isoformat()} '
            f'{created.time().isoformat(timespec="minutes")} '
            f'({self.object})'
        )

    def get_absolute_url(self) -> None:
        # Audit trails are only visible in the list view.
        return None
