from netbox.views import generic
from utilities.utils import count_related
from .. import filtersets, forms, models, tables

__all__ = (
    'InventoryItemTypeView',
    'InventoryItemTypeListView',
    'InventoryItemTypeEditView',
    'InventoryItemTypeDeleteView',
    'InventoryItemTypeBulkImportView',
    'InventoryItemTypeBulkEditView',
    'InventoryItemTypeBulkDeleteView',
)

class InventoryItemTypeView(generic.ObjectView):
    queryset = models.InventoryItemType.objects.all()

    def get_extra_context(self, request, instance):
        context = super().get_extra_context(request, instance)
        context['asset_count'] = models.Asset.objects.restrict(request.user, 'view').filter(inventoryitem_type=instance).count()
        return context


class InventoryItemTypeListView(generic.ObjectListView):
    queryset = models.InventoryItemType.objects.annotate(
        asset_count=count_related(models.Asset, 'inventoryitem_type'),
    )
    table = tables.InventoryItemTypeTable
    filterset = filtersets.InventoryItemTypeFilterSet
    filterset_form = forms.InventoryItemTypeFilterForm


class InventoryItemTypeEditView(generic.ObjectEditView):
    queryset = models.InventoryItemType.objects.all()
    form = forms.InventoryItemTypeForm


class InventoryItemTypeDeleteView(generic.ObjectDeleteView):
    queryset = models.InventoryItemType.objects.all()


class InventoryItemTypeBulkImportView(generic.BulkImportView):
    queryset = models.InventoryItemType.objects.all()
    model_form = forms.InventoryItemTypeImportForm


class InventoryItemTypeBulkEditView(generic.BulkEditView):
    queryset = models.InventoryItemType.objects.all()
    filterset = filtersets.InventoryItemTypeFilterSet
    table = tables.InventoryItemTypeTable
    form = forms.InventoryItemTypeBulkEditForm


class InventoryItemTypeBulkDeleteView(generic.BulkDeleteView):
    queryset = models.InventoryItemType.objects.all()
    table = tables.InventoryItemTypeTable
