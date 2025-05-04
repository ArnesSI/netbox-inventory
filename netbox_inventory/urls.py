from django.urls import include, path

from utilities.urls import get_model_urls

from . import views

urlpatterns = (
    # InventoryItemGroups
    path(
        'inventory-item-groups/',
        include(get_model_urls('netbox_inventory', 'inventoryitemgroup', detail=False)),
    ),
    path(
        'inventory-item-groups/<int:pk>/',
        include(get_model_urls('netbox_inventory', 'inventoryitemgroup')),
    ),
    # InventoryItemTypes
    path(
        'inventory-item-types/',
        include(get_model_urls('netbox_inventory', 'inventoryitemtype', detail=False)),
    ),
    path(
        'inventory-item-types/<int:pk>/',
        include(get_model_urls('netbox_inventory', 'inventoryitemtype')),
    ),
    # Assets
    path(
        'assets/',
        include(get_model_urls('netbox_inventory', 'asset', detail=False)),
    ),
    path(
        'assets/<int:pk>/',
        include(get_model_urls('netbox_inventory', 'asset')),
    ),
    path(
        'assets/<int:pk>/assign/',
        views.AssetAssignView.as_view(),
        name='asset_assign',
    ),
    path(
        'assets/device/create/',
        views.AssetDeviceCreateView.as_view(),
        name='asset_device_create',
    ),
    path(
        'assets/module/create/',
        views.AssetModuleCreateView.as_view(),
        name='asset_module_create',
    ),
    path(
        'assets/inventory-item/create/',
        views.AssetInventoryItemCreateView.as_view(),
        name='asset_inventoryitem_create',
    ),
    path(
        'assets/rack/create/',
        views.AssetRackCreateView.as_view(),
        name='asset_rack_create',
    ),
    path(
        'assets/device/<int:pk>/reassign/',
        views.AssetDeviceReassignView.as_view(),
        name='asset_device_reassign',
    ),
    path(
        'assets/module/<int:pk>/reassign/',
        views.AssetModuleReassignView.as_view(),
        name='asset_module_reassign',
    ),
    path(
        'assets/inventoryitem/<int:pk>/reassign/',
        views.AssetInventoryItemReassignView.as_view(),
        name='asset_inventoryitem_reassign',
    ),
    path(
        'assets/rack/<int:pk>/reassign/',
        views.AssetRackReassignView.as_view(),
        name='asset_rack_reassign',
    ),
    # Suppliers
    path(
        'suppliers/',
        include(get_model_urls('netbox_inventory', 'supplier', detail=False)),
    ),
    path(
        'suppliers/<int:pk>/',
        include(get_model_urls('netbox_inventory', 'supplier')),
    ),
    # Purchases
    path(
        'purchases/',
        include(get_model_urls('netbox_inventory', 'purchase', detail=False)),
    ),
    path(
        'purchases/<int:pk>/',
        include(get_model_urls('netbox_inventory', 'purchase')),
    ),
    # Deliveries
    path(
        'deliveries/',
        include(get_model_urls('netbox_inventory', 'delivery', detail=False)),
    ),
    path(
        'deliveries/<int:pk>/',
        include(get_model_urls('netbox_inventory', 'delivery')),
    ),
    # AuditFlows (for clarity above AuditFlowPages)
    path(
        'audit-flows/',
        include(get_model_urls('netbox_inventory', 'auditflow', detail=False)),
    ),
    path(
        'audit-flows/<int:pk>/',
        include(get_model_urls('netbox_inventory', 'auditflow')),
    ),
    # AuditFlowPages
    path(
        'audit-flowpages/',
        include(get_model_urls('netbox_inventory', 'auditflowpage', detail=False)),
    ),
    path(
        'audit-flowpages/<int:pk>/',
        include(get_model_urls('netbox_inventory', 'auditflowpage')),
    ),
    # AuditFlowPageAssignments
    path(
        'audit-flowpage-assignments/',
        include(
            get_model_urls('netbox_inventory', 'auditflowpageassignment', detail=False)
        ),
    ),
    path(
        'audit-flowpage-assignments/<int:pk>/',
        include(get_model_urls('netbox_inventory', 'auditflowpageassignment')),
    ),
    # AuditTrailSources
    path(
        'audit-trail-sources/',
        include(get_model_urls('netbox_inventory', 'audittrailsource', detail=False)),
    ),
    path(
        'audit-trail-sources/<int:pk>/',
        include(get_model_urls('netbox_inventory', 'audittrailsource')),
    ),
    # AuditTrails
    path(
        'audit-trails/',
        include(get_model_urls('netbox_inventory', 'audittrail', detail=False)),
    ),
    path(
        'audit-trails/<int:pk>/',
        include(get_model_urls('netbox_inventory', 'audittrail')),
    ),
)
