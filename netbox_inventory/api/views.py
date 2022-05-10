from dcim.api.views import DeviceViewSet
from netbox.api.viewsets import NetBoxModelViewSet
from utilities.utils import count_related
from .. import filtersets, models
from .serializers import AssetSerializer, InventoryItemTypeSerializer, SupplierSerializer


class AssetViewSet(NetBoxModelViewSet):
    queryset = models.Asset.objects.prefetch_related(
        'device_type', 'device', 'module_type', 'module', 'storage_location', 'tags'
    )
    serializer_class = AssetSerializer
    filterset_class = filtersets.AssetFilterSet


class DeviceAssetViewSet(DeviceViewSet):
    """Adds option to filter on asset assignemnet"""
    filterset_class = filtersets.DeviceAssetFilterSet


class SupplierViewSet(NetBoxModelViewSet):
    queryset = models.Supplier.objects.prefetch_related('tags').annotate(
        asset_count=count_related(models.Asset, 'supplier')
    )
    serializer_class = SupplierSerializer
    filterset_class = filtersets.SupplierFilterSet


class InventoryItemTypeViewSet(NetBoxModelViewSet):
    queryset = models.InventoryItemType.objects.prefetch_related('tags').annotate(
        asset_count=count_related(models.Asset, 'inventoryitem_type')
    )
    serializer_class = InventoryItemTypeSerializer
    filterset_class = filtersets.InventoryItemTypeFilterSet
