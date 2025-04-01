from core.models import ObjectType
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer

from netbox_inventory.models import AuditFlow, AuditFlowPage, AuditFlowPageAssignment

__all__ = (
    'AuditFlowPageAssignmentSerializer',
    'AuditFlowPageSerializer',
    'AuditFlowSerializer',
)


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


class AuditFlowSerializer(BaseFlowSerializer):
    class Meta(BaseFlowSerializer.Meta):
        model = AuditFlow
        fields = BaseFlowSerializer.Meta.fields + ('enabled',)


class AuditFlowPageAssignmentSerializer(NetBoxModelSerializer):
    flow = AuditFlowSerializer(
        nested=True,
    )
    page = AuditFlowPageSerializer(
        nested=True,
    )

    class Meta:
        model = AuditFlowPageAssignment
        fields = (
            'id',
            'url',
            'display',
            'flow',
            'page',
            'weight',
            'created',
            'last_updated',
        )
        brief_fields = (
            'id',
            'url',
            'display',
            'flow',
            'page',
        )
