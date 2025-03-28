from django.core.exceptions import FieldError, ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import ObjectType
from utilities.query import dict_to_filter_params

from .mixins import NamedModel

__all__ = ('AuditFlowPage',)


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
    An `AuditFlowPage' defines a specific page in the audit flow. It is used to display
    a specific type of asset to be audited.
    """

    pass
