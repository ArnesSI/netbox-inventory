from core.models import ObjectType
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer

from netbox_inventory.models import AuditFlowPage

__all__ = ('AuditFlowPageSerializer',)


class BaseFlowSerializer(NetBoxModelSerializer):
    """
    Internal base serializer for audit flow models.
    """

    object_type = ContentTypeField(
        queryset=ObjectType.objects.all(),
    )

    class Meta:
        fields = (
            'id',
            'url',
            'display_url',
            'display',
            'name',
            'description',
            'object_type',
            'object_filter',
            'comments',
            'tags',
            'custom_fields',
            'created',
            'last_updated',
        )
        brief_fields = (
            'id',
            'url',
            'display',
            'name',
        )


class AuditFlowPageSerializer(BaseFlowSerializer):
    class Meta(BaseFlowSerializer.Meta):
        model = AuditFlowPage
