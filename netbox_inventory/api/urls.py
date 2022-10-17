from netbox.api.routers import NetBoxRouter
from . import views


app_name = 'netbox_inventory'

router = NetBoxRouter()
router.register('assets', views.AssetViewSet)
router.register('inventory-item-types', views.InventoryItemTypeViewSet)
router.register('suppliers', views.SupplierViewSet)
router.register('purchases', views.PurchaseViewSet)
router.register('devices', views.DeviceAssetViewSet)

urlpatterns = router.urls
