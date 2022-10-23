from netbox.api.routers import NetBoxRouter
from . import views


app_name = 'netbox_inventory'

router = NetBoxRouter()
router.register('assets', views.AssetViewSet)
router.register('inventory-item-types', views.InventoryItemTypeViewSet)
router.register('suppliers', views.SupplierViewSet)
router.register('purchases', views.PurchaseViewSet)
router.register('dcim/devices', views.DeviceAssetViewSet)
router.register('dcim/modules', views.ModuleAssetViewSet)
router.register('dcim/inventory-items', views.InventoryItemAssetViewSet)

urlpatterns = router.urls
