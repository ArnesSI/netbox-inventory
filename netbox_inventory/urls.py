from django.urls import include, path

from netbox.views.generic import ObjectChangeLogView, ObjectJournalView
from utilities.urls import get_model_urls
from . import models, views


urlpatterns = (

    # Assets
    path('assets/', views.AssetListView.as_view(), name='asset_list'),
    path('assets/add/', views.AssetEditView.as_view(), name='asset_add'),
    path('assets/bulk-add/', views.AssetBulkCreateView.as_view(), name='asset_bulk_add'),
    path('assets/import/', views.AssetBulkImportView.as_view(), name='asset_import'),
    path('assets/edit/', views.AssetBulkEditView.as_view(), name='asset_bulk_edit'),
    path('assets/delete/', views.AssetBulkDeleteView.as_view(), name='asset_bulk_delete'),
    path('assets/<int:pk>', views.AssetView.as_view(), name='asset'),
    path('assets/<int:pk>/edit/', views.AssetEditView.as_view(), name='asset_edit'),
    path('assets/<int:pk>/delete/', views.AssetDeleteView.as_view(), name='asset_delete'),
    path('assets/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='asset_changelog', kwargs={'model': models.Asset}),
    path('assets/<int:pk>/journal/', ObjectJournalView.as_view(), name='asset_journal', kwargs={'model': models.Asset}),
    path('assets/<int:pk>/assign/', views.AssetAssignView.as_view(), name='asset_assign'),
    path('assets/device/create/', views.AssetDeviceCreateView.as_view(), name='asset_device_create'),
    path('assets/module/create/', views.AssetModuleCreateView.as_view(), name='asset_module_create'),
    path('assets/inventory-item/create/', views.AssetInventoryItemCreateView.as_view(), name='asset_inventoryitem_create'),
    path('assets/rack/create/', views.AssetRackCreateView.as_view(), name='asset_rack_create'),
    path('assets/device/<int:pk>/reassign/', views.AssetDeviceReassignView.as_view(), name='asset_device_reassign'),
    path('assets/module/<int:pk>/reassign/', views.AssetModuleReassignView.as_view(), name='asset_module_reassign'),
    path('assets/inventoryitem/<int:pk>/reassign/', views.AssetInventoryItemReassignView.as_view(), name='asset_inventoryitem_reassign'),
    path('assets/rack/<int:pk>/reassign/', views.AssetRackReassignView.as_view(), name='asset_rack_reassign'),

    # Suppliers
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/add/', views.SupplierEditView.as_view(), name='supplier_add'),
    path('suppliers/import/', views.SupplierBulkImportView.as_view(), name='supplier_import'),
    path('suppliers/edit/', views.SupplierBulkEditView.as_view(), name='supplier_bulk_edit'),
    path('suppliers/delete/', views.SupplierBulkDeleteView.as_view(), name='supplier_bulk_delete'),
    path('suppliers/<int:pk>', views.SupplierView.as_view(), name='supplier'),
    path('suppliers/<int:pk>/', include(get_model_urls('netbox_inventory', 'supplier'))),

    # Purchases
    path('purchases/', views.PurchaseListView.as_view(), name='purchase_list'),
    path('purchases/add/', views.PurchaseEditView.as_view(), name='purchase_add'),
    path('purchases/import/', views.PurchaseBulkImportView.as_view(), name='purchase_import'),
    path('purchases/edit/', views.PurchaseBulkEditView.as_view(), name='purchase_bulk_edit'),
    path('purchases/delete/', views.PurchaseBulkDeleteView.as_view(), name='purchase_bulk_delete'),
    path('purchases/<int:pk>', views.PurchaseView.as_view(), name='purchase'),
    path('purchases/<int:pk>/edit/', views.PurchaseEditView.as_view(), name='purchase_edit'),
    path('purchases/<int:pk>/delete/', views.PurchaseDeleteView.as_view(), name='purchase_delete'),
    path('purchases/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='purchase_changelog', kwargs={'model': models.Purchase}),
    path('purchases/<int:pk>/journal/', ObjectJournalView.as_view(), name='purchase_journal', kwargs={'model': models.Purchase}),

    # Deliveries
    path('deliveries/', views.DeliveryListView.as_view(), name='delivery_list'),
    path('deliveries/add/', views.DeliveryEditView.as_view(), name='delivery_add'),
    path('deliveries/import/', views.DeliveryBulkImportView.as_view(), name='delivery_import'),
    path('deliveries/edit/', views.DeliveryBulkEditView.as_view(), name='delivery_bulk_edit'),
    path('deliveries/delete/', views.DeliveryBulkDeleteView.as_view(), name='delivery_bulk_delete'),
    path('deliveries/<int:pk>', views.DeliveryView.as_view(), name='delivery'),
    path('deliveries/<int:pk>/edit/', views.DeliveryEditView.as_view(), name='delivery_edit'),
    path('deliveries/<int:pk>/delete/', views.DeliveryDeleteView.as_view(), name='delivery_delete'),
    path('deliveries/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='delivery_changelog', kwargs={'model': models.Delivery}),
    path('deliveries/<int:pk>/journal/', ObjectJournalView.as_view(), name='delivery_journal', kwargs={'model': models.Delivery}),

    # InventoryItemTypes
    path('inventory-item-types/', views.InventoryItemTypeListView.as_view(), name='inventoryitemtype_list'),
    path('inventory-item-types/add/', views.InventoryItemTypeEditView.as_view(), name='inventoryitemtype_add'),
    path('inventory-item-types/import/', views.InventoryItemTypeBulkImportView.as_view(), name='inventoryitemtype_import'),
    path('inventory-item-types/edit/', views.InventoryItemTypeBulkEditView.as_view(), name='inventoryitemtype_bulk_edit'),
    path('inventory-item-types/delete/', views.InventoryItemTypeBulkDeleteView.as_view(), name='inventoryitemtype_bulk_delete'),
    path('inventory-item-types/<int:pk>', views.InventoryItemTypeView.as_view(), name='inventoryitemtype'),
    path('inventory-item-types/<int:pk>/edit/', views.InventoryItemTypeEditView.as_view(), name='inventoryitemtype_edit'),
    path('inventory-item-types/<int:pk>/delete/', views.InventoryItemTypeDeleteView.as_view(), name='inventoryitemtype_delete'),
    path('inventory-item-types/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='inventoryitemtype_changelog', kwargs={'model': models.InventoryItemType}),

    # InventoryItemGroups
    path('inventory-item-groups/', views.InventoryItemGroupListView.as_view(), name='inventoryitemgroup_list'),
    path('inventory-item-groups/add/', views.InventoryItemGroupEditView.as_view(), name='inventoryitemgroup_add'),
    path('inventory-item-groups/import/', views.InventoryItemGroupBulkImportView.as_view(), name='inventoryitemgroup_import'),
    path('inventory-item-groups/edit/', views.InventoryItemGroupBulkEditView.as_view(), name='inventoryitemgroup_bulk_edit'),
    path('inventory-item-groups/delete/', views.InventoryItemGroupBulkDeleteView.as_view(), name='inventoryitemgroup_bulk_delete'),
    path('inventory-item-groups/<int:pk>', views.InventoryItemGroupView.as_view(), name='inventoryitemgroup'),
    path('inventory-item-groups/<int:pk>/edit/', views.InventoryItemGroupEditView.as_view(), name='inventoryitemgroup_edit'),
    path('inventory-item-groups/<int:pk>/delete/', views.InventoryItemGroupDeleteView.as_view(), name='inventoryitemgroup_delete'),
    path('inventory-item-groups/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='inventoryitemgroup_changelog', kwargs={'model': models.InventoryItemGroup}),

)
