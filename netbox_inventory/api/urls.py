from netbox.api.routers import NetBoxRouter

from . import views

app_name = 'netbox_inventory'

router = NetBoxRouter()
router.APIRootView = views.NetboxInventoryRootView

# Assets
router.register('assets', views.AssetViewSet)
router.register('inventory-item-types', views.InventoryItemTypeViewSet)
router.register('inventory-item-groups', views.InventoryItemGroupViewSet)
router.register('dcim/devices', views.DeviceAssetViewSet)
router.register('dcim/modules', views.ModuleAssetViewSet)
router.register('dcim/inventory-items', views.InventoryItemAssetViewSet)

# Deliveries
router.register('suppliers', views.SupplierViewSet)
router.register('purchases', views.PurchaseViewSet)
router.register('deliveries', views.DeliveryViewSet)

# Audit
router.register('audit-flows', views.AuditFlowViewSet)
router.register('audit-flowpages', views.AuditFlowPageViewSet)
router.register('audit-flowpage-assignments', views.AuditFlowPageAssignmentViewSet)
router.register('audit-trail-sources', views.AuditTrailSourceViewSet)
router.register('audit-trails', views.AuditTrailViewSet)


urlpatterns = router.urls
