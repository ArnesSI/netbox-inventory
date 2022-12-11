from netbox.views import generic
from utilities.utils import count_related
from .. import filtersets, forms, models, tables

__all__ = (
    'InventoryItemGroupView',
    'InventoryItemGroupListView',
    'InventoryItemGroupEditView',
    'InventoryItemGroupDeleteView',
    #'InventoryItemGroupBulkImportView',
    #'InventoryItemGroupBulkEditView',
    'InventoryItemGroupBulkDeleteView',
)

class InventoryItemGroupView(generic.ObjectView):
    queryset = models.InventoryItemGroup.objects.all()


class InventoryItemGroupListView(generic.ObjectListView):
    queryset = models.InventoryItemGroup.objects.annotate(
        inventoryitemtype_count=count_related(models.InventoryItemType, 'inventoryitem_group'),
        asset_count=count_related(models.Asset, 'inventoryitem_type__inventoryitem_group'),
    )
    table = tables.InventoryItemGroupTable
    filterset = filtersets.InventoryItemGroupFilterSet
    filterset_form = forms.InventoryItemGroupFilterForm


class InventoryItemGroupEditView(generic.ObjectEditView):
    queryset = models.InventoryItemGroup.objects.all()
    form = forms.InventoryItemGroupForm


class InventoryItemGroupDeleteView(generic.ObjectDeleteView):
    queryset = models.InventoryItemGroup.objects.all()


# class InventoryItemGroupBulkImportView(generic.BulkImportView):
#     queryset = models.InventoryItemGroup.objects.all()   
#     table = tables.InventoryItemGroupTable 
#     model_form = forms.InventoryItemGroupCSVForm


# class InventoryItemGroupBulkEditView(generic.BulkEditView):
#     queryset = models.InventoryItemGroup.objects.all()
#     filterset = filtersets.InventoryItemGroupFilterSet
#     table = tables.InventoryItemGroupTable
#     form = forms.InventoryItemGroupBulkEditForm


class InventoryItemGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = models.InventoryItemGroup.objects.all()
    table = tables.InventoryItemGroupTable
