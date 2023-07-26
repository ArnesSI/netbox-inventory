from rest_framework import serializers

from dcim.api.serializers import (
    NestedDeviceTypeSerializer, NestedDeviceSerializer,
    NestedManufacturerSerializer,
    NestedModuleTypeSerializer, NestedModuleSerializer,
    NestedInventoryItemSerializer, NestedLocationSerializer
)
from tenancy.api.serializers import NestedContactSerializer, NestedTenantSerializer
from netbox.api.serializers import NetBoxModelSerializer
from .nested_serializers import *
from ..models import Asset, Delivery, InventoryItemType, InventoryItemGroup, Purchase, Supplier


class AssetSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:asset-detail'
    )
    device_type = NestedDeviceTypeSerializer(required=False, allow_null=True, default=None)
    device = NestedDeviceSerializer(required=False, allow_null=True, default=None)
    module_type = NestedModuleTypeSerializer(required=False, allow_null=True, default=None)
    module = NestedModuleSerializer(required=False, allow_null=True, default=None)
    inventoryitem_type = NestedInventoryItemTypeSerializer(required=False, allow_null=True, default=None) 
    inventoryitem = NestedInventoryItemSerializer(required=False, allow_null=True, default=None)
    storage_location = NestedLocationSerializer(required=False, allow_null=True, default=None)
    delivery = NestedDeliverySerializer(required=False, allow_null=True, default=None)
    purchase = NestedPurchaseSerializer(required=False, allow_null=True, default=None)
    tenant = NestedTenantSerializer(required=False, allow_null=True, default=None)
    contact = NestedContactSerializer(required=False, allow_null=True, default=None)
    owner = NestedTenantSerializer(required=False, allow_null=True, default=None)

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
            'id', 'url', 'display', 'name', 'asset_tag', 'serial', 'status',
            'kind', 'device_type', 'device', 'module_type', 'module', 'inventoryitem_type','inventoryitem', 
            'tenant', 'contact', 'storage_location', 'owner', 'delivery', 'purchase',
            'warranty_start', 'warranty_end',
            'comments', 'tags', 'custom_fields', 'created', 'last_updated'
        )
        # DRF autiomatically creates validator from model's unique_together contraints
        # that doesn't work if we allow some filelds in a unique_together to be null
        # so we remove DRF's auto generated validators and rely on model's validation
        # logic to handle validation
        # see  https://www.django-rest-framework.org/api-guide/validators/#optional-fields
        validators = []


class SupplierSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:supplier-detail'
    )
    asset_count = serializers.IntegerField(read_only=True)
    purchase_count = serializers.IntegerField(read_only=True)
    delivery_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Supplier
        fields = (
            'id', 'url', 'display', 'name', 'slug', 'description', 'comments',
            'tags', 'custom_fields', 'created', 'last_updated', 'asset_count',
            'purchase_count', 'delivery_count',
        )


class PurchaseSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:purchase-detail'
    )
    supplier = NestedSupplierSerializer()
    asset_count = serializers.IntegerField(read_only=True)
    delivery_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Purchase
        fields = (
            'id', 'url', 'display', 'supplier', 'name', 'date', 'description',
            'comments', 'tags', 'custom_fields', 'created', 'last_updated',
            'asset_count', 'delivery_count',
        )


class DeliverySerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:delivery-detail'
    )
    purchase = NestedPurchaseSerializer()
    receiving_contact = NestedContactSerializer(required=False, allow_null=True, default=None)
    asset_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Delivery
        fields = (
            'id', 'url', 'display', 'purchase', 'name', 'date', 'description', 'comments',
            'receiving_contact', 'tags', 'custom_fields', 'created', 'last_updated', 'asset_count',
        )


class InventoryItemTypeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:inventoryitemtype-detail'
    )
    manufacturer = NestedManufacturerSerializer()
    inventoryitem_group = NestedInventoryItemGroupSerializer(required=False, allow_null=True, default=None)
    asset_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = InventoryItemType
        fields = (
            'id', 'url', 'display', 'model', 'slug', 'manufacturer', 'part_number',
            'inventoryitem_group', 'comments', 'tags', 'custom_fields', 'created',
            'last_updated', 'asset_count',
        )


class InventoryItemGroupSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:inventoryitemgroup-detail'
    )
    parent = NestedInventoryItemGroupSerializer(required=False, allow_null=True, default=None)
    asset_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = InventoryItemGroup
        fields = (
            'id', 'url', 'display', 'name', 'parent', 'comments', 'tags', 'custom_fields',
            'created', 'last_updated', 'asset_count',
        )
