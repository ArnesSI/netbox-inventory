from rest_framework import serializers

from dcim.api.serializers import (
    DeviceSerializer,
    DeviceTypeSerializer,
    InventoryItemSerializer,
    LocationSerializer,
    ManufacturerSerializer,
    ModuleSerializer,
    ModuleTypeSerializer,
    RackSerializer,
    RackTypeSerializer,
)
from netbox.api.serializers import NestedGroupModelSerializer, NetBoxModelSerializer
from tenancy.api.serializers import ContactSerializer, TenantSerializer

from .deliveries import *
from .nested import *
from netbox_inventory.models import Asset, InventoryItemGroup, InventoryItemType


class InventoryItemGroupSerializer(NestedGroupModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:inventoryitemgroup-detail'
    )
    parent = NestedInventoryItemGroupSerializer(
        required=False, allow_null=True, default=None
    )
    asset_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = InventoryItemGroup
        fields = (
            'id',
            'url',
            'display',
            'name',
            'parent',
            'description',
            'comments',
            'tags',
            'custom_fields',
            'created',
            'last_updated',
            'asset_count',
            '_depth',
        )
        brief_fields = ('id', 'url', 'display', 'name', 'description', '_depth')


class InventoryItemTypeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:inventoryitemtype-detail'
    )
    manufacturer = ManufacturerSerializer(nested=True)
    inventoryitem_group = InventoryItemGroupSerializer(
        nested=True, required=False, allow_null=True, default=None
    )
    asset_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = InventoryItemType
        fields = (
            'id',
            'url',
            'display',
            'model',
            'slug',
            'manufacturer',
            'part_number',
            'inventoryitem_group',
            'description',
            'comments',
            'tags',
            'custom_fields',
            'created',
            'last_updated',
            'asset_count',
        )
        brief_fields = (
            'id',
            'url',
            'display',
            'manufacturer',
            'model',
            'slug',
            'description',
        )


class AssetSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:asset-detail'
    )
    device_type = DeviceTypeSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None,
    )
    device = DeviceSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None,
    )
    module_type = ModuleTypeSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None,
    )
    module = ModuleSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None,
    )
    inventoryitem_type = InventoryItemTypeSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None,
    )
    inventoryitem = InventoryItemSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None,
    )
    rack_type = RackTypeSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None,
    )
    rack = RackSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None,
    )
    storage_location = LocationSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None,
    )
    delivery = DeliverySerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None,
    )
    purchase = PurchaseSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None,
    )
    tenant = TenantSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None,
    )
    contact = ContactSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None,
    )
    owner = TenantSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None,
    )

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        # if only delivery set, infer pruchase from it
        if 'delivery' in ret and ret['delivery'] and not ret.get('purchase'):
            ret['purchase'] = ret['delivery'].purchase
        if 'asset_tag' in ret and ret['asset_tag'] == '':
            ret['asset_tag'] = None
        if 'serial' in ret and ret['serial'] == '':
            ret['serial'] = None
        return ret

    class Meta:
        model = Asset
        fields = (
            'id',
            'url',
            'display',
            'name',
            'description',
            'asset_tag',
            'serial',
            'status',
            'kind',
            'device_type',
            'device',
            'module_type',
            'module',
            'inventoryitem_type',
            'inventoryitem',
            'rack_type',
            'rack',
            'tenant',
            'contact',
            'storage_location',
            'owner',
            'delivery',
            'purchase',
            'warranty_start',
            'warranty_end',
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
            'serial',
            'name',
            'description',
        )
        # DRF autiomatically creates validator from model's unique_together contraints
        # that doesn't work if we allow some filelds in a unique_together to be null
        # so we remove DRF's auto generated validators and rely on model's validation
        # logic to handle validation
        # see  https://www.django-rest-framework.org/api-guide/validators/#optional-fields
        validators = []
