from rest_framework import serializers

from dcim.api.serializers import (
    NestedDeviceTypeSerializer, NestedDeviceSerializer,
    NestedManufacturerSerializer,
    NestedModuleTypeSerializer, NestedModuleSerializer
)
from netbox.api.serializers import NetBoxModelSerializer
from .nested_serializers import *
from ..models import Asset, InventoryItemType, InventoryItemGroup, Purchase, Supplier



class AssetSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:asset-detail'
    )
    device_type = NestedDeviceTypeSerializer()
    device = NestedDeviceSerializer()
    module_type = NestedModuleTypeSerializer()
    module = NestedModuleSerializer()
    storage_location = NestedModuleSerializer()
    purchase = NestedPurchaseSerializer()

    class Meta:
        model = Asset
        fields = (
            'id', 'url', 'display', 'name', 'asset_tag', 'serial', 'status',
            'kind', 'device_type', 'device', 'module_type', 'module',
            'tenant', 'contact', 'storage_location', 'owner', 'purchase',
            'warranty_start', 'warranty_end',
            'comments', 'tags', 'custom_fields', 'created', 'last_updated'
        )


class SupplierSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:supplier-detail'
    )
    asset_count = serializers.IntegerField(read_only=True)
    purchase_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Supplier
        fields = (
            'id', 'url', 'display', 'name', 'slug', 'description', 'comments',
            'tags', 'custom_fields', 'created', 'last_updated', 'asset_count',
            'purchase_count',
        )


class PurchaseSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:purchase-detail'
    )
    supplier = NestedSupplierSerializer()
    asset_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Purchase
        fields = (
            'id', 'url', 'display', 'supplier', 'name', 'date', 'description', 'comments',
            'tags', 'custom_fields', 'created', 'last_updated', 'asset_count',
        )


class InventoryItemTypeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:inventoryitemtype-detail'
    )
    manufacturer = NestedManufacturerSerializer()
    inventoryitem_group = NestedInventoryItemGroupSerializer()
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
    inventoryitemtype_count = serializers.IntegerField(read_only=True)
    asset_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = InventoryItemGroup
        fields = (
            'id', 'url', 'display', 'name', 'comments', 'tags', 'custom_fields',
            'created', 'last_updated', 'inventoryitemtype_count', 'asset_count',
        )
