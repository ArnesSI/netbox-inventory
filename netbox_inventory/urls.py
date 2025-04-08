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
    path('assets/bulk-assign/',
        views.AssetBulkAssignView.as_view(),
        name='asset_bulk_assign'
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
    # BOMs
    path(
        'boms/',
        include(get_model_urls('netbox_inventory', 'bom', detail=False)),
    ),
    path(
        'boms/<int:pk>/',
        include(get_model_urls('netbox_inventory', 'bom')),
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
    # Couriers
    path(
        'couriers/',
        include(get_model_urls('netbox_inventory', 'courier', detail=False)),
    ),
    path(
        'couriers/<int:pk>/',
        include(get_model_urls('netbox_inventory', 'courier')),
    ),
    # Transfers
    path(
        'transfers/',
        include(get_model_urls('netbox_inventory', 'transfer', detail=False)),
    ),
    path(
        'transfers/<int:pk>/',
        include(get_model_urls('netbox_inventory', 'transfer')),
    ),
)
