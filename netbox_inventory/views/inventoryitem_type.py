from netbox.views import generic
from utilities.query import count_related
from utilities.views import register_model_view

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


@register_model_view(models.InventoryItemType)
class InventoryItemTypeView(generic.ObjectView):
    queryset = models.InventoryItemType.objects.all()

    def get_extra_context(self, request, instance):
        context = super().get_extra_context(request, instance)
        context['asset_count'] = (
            models.Asset.objects.restrict(request.user, 'view')
            .filter(inventoryitem_type=instance)
            .count()
        )
        return context


@register_model_view(models.InventoryItemType, 'list', path='', detail=False)
class InventoryItemTypeListView(generic.ObjectListView):
    queryset = models.InventoryItemType.objects.annotate(
        asset_count=count_related(models.Asset, 'inventoryitem_type'),
    )
    table = tables.InventoryItemTypeTable
    filterset = filtersets.InventoryItemTypeFilterSet
    filterset_form = forms.InventoryItemTypeFilterForm


@register_model_view(models.InventoryItemType, 'edit')
@register_model_view(models.InventoryItemType, 'add', detail=False)
class InventoryItemTypeEditView(generic.ObjectEditView):
    queryset = models.InventoryItemType.objects.all()
    form = forms.InventoryItemTypeForm


@register_model_view(models.InventoryItemType, 'delete')
class InventoryItemTypeDeleteView(generic.ObjectDeleteView):
    queryset = models.InventoryItemType.objects.all()


@register_model_view(
    models.InventoryItemType, 'bulk_import', path='import', detail=False
)
class InventoryItemTypeBulkImportView(generic.BulkImportView):
    queryset = models.InventoryItemType.objects.all()
    model_form = forms.InventoryItemTypeImportForm


@register_model_view(models.InventoryItemType, 'bulk_edit', path='edit', detail=False)
class InventoryItemTypeBulkEditView(generic.BulkEditView):
    queryset = models.InventoryItemType.objects.all()
    filterset = filtersets.InventoryItemTypeFilterSet
    table = tables.InventoryItemTypeTable
    form = forms.InventoryItemTypeBulkEditForm


@register_model_view(
    models.InventoryItemType, 'bulk_delete', path='delete', detail=False
)
class InventoryItemTypeBulkDeleteView(generic.BulkDeleteView):
    queryset = models.InventoryItemType.objects.all()
    filterset = filtersets.InventoryItemTypeFilterSet
    table = tables.InventoryItemTypeTable
