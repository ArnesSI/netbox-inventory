from netbox.views import generic
from utilities.query import count_related
from utilities.views import register_model_view

from .. import filtersets, forms, models, tables

__all__ = (
    'PurchaseView',
    'PurchaseListView',
    'PurchaseEditView',
    'PurchaseDeleteView',
    'PurchaseBulkImportView',
    'PurchaseBulkEditView',
    'PurchaseBulkDeleteView',
)


@register_model_view(models.Purchase)
class PurchaseView(generic.ObjectView):
    queryset = models.Purchase.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'asset_count': models.Asset.objects.filter(purchase=instance).count(),
            'delivery_count': models.Delivery.objects.filter(purchase=instance).count(),
        }


@register_model_view(models.Purchase, 'list', path='', detail=False)
class PurchaseListView(generic.ObjectListView):
    queryset = models.Purchase.objects.annotate(
        asset_count=count_related(models.Asset, 'purchase'),
        delivery_count=count_related(models.Delivery, 'purchase'),
    )
    table = tables.PurchaseTable
    filterset = filtersets.PurchaseFilterSet
    filterset_form = forms.PurchaseFilterForm


@register_model_view(models.Purchase, 'edit')
@register_model_view(models.Purchase, 'add', detail=False)
class PurchaseEditView(generic.ObjectEditView):
    queryset = models.Purchase.objects.all()
    form = forms.PurchaseForm


@register_model_view(models.Purchase, 'delete')
class PurchaseDeleteView(generic.ObjectDeleteView):
    queryset = models.Purchase.objects.all()


@register_model_view(models.Purchase, 'bulk_import', path='import', detail=False)
class PurchaseBulkImportView(generic.BulkImportView):
    queryset = models.Purchase.objects.all()
    model_form = forms.PurchaseImportForm


@register_model_view(models.Purchase, 'bulk_edit', path='edit', detail=False)
class PurchaseBulkEditView(generic.BulkEditView):
    queryset = models.Purchase.objects.all()
    filterset = filtersets.PurchaseFilterSet
    table = tables.PurchaseTable
    form = forms.PurchaseBulkEditForm


@register_model_view(models.Purchase, 'bulk_delete', path='delete', detail=False)
class PurchaseBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Purchase.objects.all()
    filterset = filtersets.PurchaseFilterSet
    table = tables.PurchaseTable
