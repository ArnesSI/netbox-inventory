from rest_framework import serializers

from dcim.api.serializers import NestedManufacturerSerializer
from netbox.api.serializers import WritableNestedSerializer
from ..models import Asset, InventoryItemType, Purchase, Supplier

__all__ = (
    'NestedAssetSerializer',
    'NestedSupplierSerializer',
    'NestedPurchaseSerializer',
    'NestedInventoryItemTypeSerializer',
)


class NestedAssetSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:asset-detail'
    )

    class Meta:
        model = Asset
        fields = ('id', 'url', 'display', 'serial')


class NestedSupplierSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:supplier-detail'
    )

    class Meta:
        model = Supplier
        fields = ('id', 'url', 'display', 'name', 'slug')


class NestedPurchaseSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:purchase-detail'
    )
    supplier = NestedSupplierSerializer()

    class Meta:
        model = Purchase
        fields = ('id', 'url', 'display', 'supplier', 'name', 'date')


class NestedInventoryItemTypeSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:inventoryitemtype-detail'
    )
    manufacturer = NestedManufacturerSerializer()

    class Meta:
        model = InventoryItemType
        fields = ('id', 'url', 'display', 'manufacturer', 'model', 'slug')
