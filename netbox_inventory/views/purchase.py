from netbox.views import generic
from utilities.query import count_related
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

class PurchaseView(generic.ObjectView):
    queryset = models.Purchase.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'asset_count': models.Asset.objects.filter(purchase=instance).count(),
            'delivery_count': models.Delivery.objects.filter(purchase=instance).count(),
        }

class PurchaseListView(generic.ObjectListView):
    queryset = models.Purchase.objects.annotate(
        asset_count=count_related(models.Asset, 'purchase'),
        delivery_count=count_related(models.Delivery, 'purchase'),
    )
    table = tables.PurchaseTable
    filterset = filtersets.PurchaseFilterSet
    filterset_form = forms.PurchaseFilterForm


class PurchaseEditView(generic.ObjectEditView):
    queryset = models.Purchase.objects.all()
    form = forms.PurchaseForm


class PurchaseDeleteView(generic.ObjectDeleteView):
    queryset = models.Purchase.objects.all()


class PurchaseBulkImportView(generic.BulkImportView):
    queryset = models.Purchase.objects.all()
    model_form = forms.PurchaseImportForm


class PurchaseBulkEditView(generic.BulkEditView):
    queryset = models.Purchase.objects.all()
    filterset = filtersets.PurchaseFilterSet
    table = tables.PurchaseTable
    form = forms.PurchaseBulkEditForm


class PurchaseBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Purchase.objects.all()
    table = tables.PurchaseTable
