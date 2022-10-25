from django.urls import path

from netbox.views.generic import ObjectChangeLogView, ObjectJournalView
from . import models, views


urlpatterns = (

    # Assets
    path('assets/', views.AssetListView.as_view(), name='asset_list'),
    path('assets/add/', views.AssetEditView.as_view(), name='asset_add'),
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

    # Suppliers
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/add/', views.SupplierEditView.as_view(), name='supplier_add'),
    #path('suppliers/import/', views.SupplierBulkImportView.as_view(), name='supplier_import'),
    #path('suppliers/edit/', views.SupplierBulkEditView.as_view(), name='supplier_bulk_edit'),
    path('suppliers/delete/', views.SupplierBulkDeleteView.as_view(), name='supplier_bulk_delete'),
    path('suppliers/<int:pk>', views.SupplierView.as_view(), name='supplier'),
    path('suppliers/<int:pk>/edit/', views.SupplierEditView.as_view(), name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),
    path('suppliers/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='supplier_changelog', kwargs={'model': models.Supplier}),
    path('suppliers/<int:pk>/journal/', ObjectJournalView.as_view(), name='supplier_journal', kwargs={'model': models.Supplier}),

    # Purchases
    path('purchases/', views.PurchaseListView.as_view(), name='purchase_list'),
    path('purchases/add/', views.PurchaseEditView.as_view(), name='purchase_add'),
    #path('purchases/import/', views.PurchaseBulkImportView.as_view(), name='purchase_import'),
    #path('purchases/edit/', views.PurchaseBulkEditView.as_view(), name='purchase_bulk_edit'),
    path('purchases/delete/', views.PurchaseBulkDeleteView.as_view(), name='purchase_bulk_delete'),
    path('purchases/<int:pk>', views.PurchaseView.as_view(), name='purchase'),
    path('purchases/<int:pk>/edit/', views.PurchaseEditView.as_view(), name='purchase_edit'),
    path('purchases/<int:pk>/delete/', views.PurchaseDeleteView.as_view(), name='purchase_delete'),
    path('purchases/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='purchase_changelog', kwargs={'model': models.Purchase}),
    path('purchases/<int:pk>/journal/', ObjectJournalView.as_view(), name='purchase_journal', kwargs={'model': models.Purchase}),

    # InventoryItemTypes
    path('inventory-item-types/', views.InventoryItemTypeListView.as_view(), name='inventoryitemtype_list'),
    path('inventory-item-types/add/', views.InventoryItemTypeEditView.as_view(), name='inventoryitemtype_add'),
    #path('inventory-item-types/import/', views.InventoryItemTypeBulkImportView.as_view(), name='inventoryitemtype_import'),
    #path('inventory-item-types/edit/', views.InventoryItemTypeBulkEditView.as_view(), name='inventoryitemtype_bulk_edit'),
    path('inventory-item-types/delete/', views.InventoryItemTypeBulkDeleteView.as_view(), name='inventoryitemtype_bulk_delete'),
    path('inventory-item-types/<int:pk>', views.InventoryItemTypeView.as_view(), name='inventoryitemtype'),
    path('inventory-item-types/<int:pk>/edit/', views.InventoryItemTypeEditView.as_view(), name='inventoryitemtype_edit'),
    path('inventory-item-types/<int:pk>/delete/', views.InventoryItemTypeDeleteView.as_view(), name='inventoryitemtype_delete'),
    path('inventory-item-types/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='inventoryitemtype_changelog', kwargs={'model': models.InventoryItemType}),

)
