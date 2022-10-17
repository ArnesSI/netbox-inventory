from netbox.views import generic
from utilities.utils import count_related
from .. import filtersets, forms, models, tables

__all__ = (
    'PurchaseView',
    'PurchaseListView',
    'PurchaseEditView',
    'PurchaseDeleteView',
    #'PurchaseBulkImportView',
    #'PurchaseBulkEditView',
    'PurchaseBulkDeleteView',
)

class PurchaseView(generic.ObjectView):
    queryset = models.Purchase.objects.all()

    def get_extra_context(self, request, instance):
        purchase_assets = models.Asset.objects.restrict(request.user, 'view').filter(
            purchase=instance
        )
        asset_table = tables.AssetTable(purchase_assets, user=request.user)
        asset_table.columns.hide('purchase')
        asset_table.columns.hide('purchase_date')
        asset_table.columns.hide('supplier')
        asset_table.configure(request)

        return {
            'asset_table': asset_table,
            'asset_count': models.Asset.objects.filter(purchase=instance).count(),
        }

class PurchaseListView(generic.ObjectListView):
    queryset = models.Purchase.objects.annotate(
        asset_count=count_related(models.Asset, 'purchase'),
    )
    table = tables.PurchaseTable
    filterset = filtersets.PurchaseFilterSet
    filterset_form = forms.PurchaseFilterForm


class PurchaseEditView(generic.ObjectEditView):
    queryset = models.Purchase.objects.all()
    form = forms.PurchaseForm


class PurchaseDeleteView(generic.ObjectDeleteView):
    queryset = models.Purchase.objects.all()


# class PurchaseBulkImportView(generic.BulkImportView):
#     queryset = models.Purchase.objects.all()   
#     table = tables.PurchaseTable 
#     model_form = forms.PurchaseCSVForm


# class PurchaseBulkEditView(generic.BulkEditView):
#     queryset = models.Purchase.objects.all()
#     filterset = filtersets.PurchaseFilterSet
#     table = tables.PurchaseTable
#     form = forms.PurchaseBulkEditForm


class PurchaseBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Purchase.objects.all()
    table = tables.PurchaseTable
