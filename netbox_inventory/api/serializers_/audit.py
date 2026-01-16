from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import ObjectType
from netbox.api.fields import ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer, PrimaryModelSerializer
from utilities.api import get_serializer_for_model

from netbox_inventory.models import (
    AuditFlow,
    AuditFlowPage,
    AuditFlowPageAssignment,
    AuditTrail,
    AuditTrailSource,
)

__all__ = (
    'AuditFlowPageAssignmentSerializer',
    'AuditFlowPageSerializer',
    'AuditFlowSerializer',
    'AuditTrailSerializer',
    'AuditTrailSourceSerializer',
)


class BaseFlowSerializer(PrimaryModelSerializer):
    """
    Internal base serializer for audit flow models.
    """

    object_type = ContentTypeField(
        queryset=ObjectType.objects.public(),
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
            'owner',
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


class AuditTrailSourceSerializer(PrimaryModelSerializer):
    class Meta:
        model = AuditTrailSource
        fields = (
            'id',
            'url',
            'display',
            'display_url',
            'name',
            'slug',
            'description',
            'owner',
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
            'slug',
        )


class AuditTrailSerializer(NetBoxModelSerializer):
    object_type = ContentTypeField(
        queryset=ObjectType.objects.public(),
    )
    object = serializers.SerializerMethodField(
        read_only=True,
    )
    source = AuditTrailSourceSerializer(
        nested=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = AuditTrail
        fields = (
            'id',
            'url',
            'display',
            'object_type',
            'object_id',
            'object',
            'source',
            'created',
            'last_updated',
        )
        brief_fields = (
            'id',
            'url',
            'display',
            'object',
        )

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_object(self, instance):
        serializer = get_serializer_for_model(instance.object_type.model_class())
        context = {'request': self.context['request']}
        return serializer(instance.object, nested=True, context=context).data
