from dcim.api.views import DeviceViewSet, InventoryItemViewSet, ModuleViewSet
from netbox.api.viewsets import NetBoxModelViewSet
from utilities.utils import count_related
from .. import filtersets, models
from .serializers import (
    AssetSerializer, InventoryItemTypeSerializer, InventoryItemGroupSerializer,
    PurchaseSerializer, SupplierSerializer
)


class AssetViewSet(NetBoxModelViewSet):
    queryset = models.Asset.objects.prefetch_related(
        'device_type', 'device', 'module_type', 'module', 'storage_location', 'purchase__supplier', 'tags'
    )
    serializer_class = AssetSerializer
    filterset_class = filtersets.AssetFilterSet


class SupplierViewSet(NetBoxModelViewSet):
    queryset = models.Supplier.objects.prefetch_related('tags').annotate(
        asset_count=count_related(models.Asset, 'purchase__supplier'),
        purchase_count=count_related(models.Purchase, 'supplier'),
    )
    serializer_class = SupplierSerializer
    filterset_class = filtersets.SupplierFilterSet


class PurchaseViewSet(NetBoxModelViewSet):
    queryset = models.Purchase.objects.prefetch_related('tags').annotate(
        asset_count=count_related(models.Asset, 'purchase')
    )
    serializer_class = PurchaseSerializer
    filterset_class = filtersets.PurchaseFilterSet


class InventoryItemTypeViewSet(NetBoxModelViewSet):
    queryset = models.InventoryItemType.objects.prefetch_related('tags').annotate(
        asset_count=count_related(models.Asset, 'inventoryitem_type')
    )
    serializer_class = InventoryItemTypeSerializer
    filterset_class = filtersets.InventoryItemTypeFilterSet


class InventoryItemGroupViewSet(NetBoxModelViewSet):
    queryset = models.InventoryItemGroup.objects.prefetch_related('tags').annotate(
        inventoryitemtype_count=count_related(models.InventoryItemType, 'inventoryitem_group'),
        asset_count=count_related(models.Asset, 'inventoryitem_type__inventoryitem_group')
    )
    serializer_class = InventoryItemGroupSerializer
    filterset_class = filtersets.InventoryItemGroupFilterSet


class DeviceAssetViewSet(DeviceViewSet):
    """Adds option to filter on asset assignemnet"""
    filterset_class = filtersets.DeviceAssetFilterSet


class ModuleAssetViewSet(ModuleViewSet):
    """Adds option to filter on asset assignemnet"""
    filterset_class = filtersets.ModuleAssetFilterSet


class InventoryItemAssetViewSet(InventoryItemViewSet):
    """Adds option to filter on asset assignemnet"""
    filterset_class = filtersets.InventoryItemAssetFilterSet
