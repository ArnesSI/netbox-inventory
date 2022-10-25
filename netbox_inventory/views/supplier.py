from netbox.views import generic
from utilities.utils import count_related
from .. import filtersets, forms, models, tables

__all__ = (
    'SupplierView',
    'SupplierListView',
    'SupplierEditView',
    'SupplierDeleteView',
    #'SupplierBulkImportView',
    #'SupplierBulkEditView',
    'SupplierBulkDeleteView',
)

class SupplierView(generic.ObjectView):
    queryset = models.Supplier.objects.all()

    def get_extra_context(self, request, instance):
        supplier_assets = models.Asset.objects.restrict(request.user, 'view').filter(
            purchase__supplier=instance
        )
        asset_table = tables.AssetTable(supplier_assets, user=request.user)
        asset_table.columns.hide('supplier')
        asset_table.configure(request)

        return {
            'asset_table': asset_table,
            'asset_count': models.Asset.objects.filter(purchase__supplier=instance).count(),
            'purchase_count': models.Purchase.objects.filter(supplier=instance).count(),
        }

class SupplierListView(generic.ObjectListView):
    queryset = models.Supplier.objects.annotate(
        purchase_count=count_related(models.Purchase, 'supplier'),
        asset_count=count_related(models.Asset, 'purchase__supplier'),
    )
    table = tables.SupplierTable
    filterset = filtersets.SupplierFilterSet
    filterset_form = forms.SupplierFilterForm


class SupplierEditView(generic.ObjectEditView):
    queryset = models.Supplier.objects.all()
    form = forms.SupplierForm


class SupplierDeleteView(generic.ObjectDeleteView):
    queryset = models.Supplier.objects.all()


# class SupplierBulkImportView(generic.BulkImportView):
#     queryset = models.Supplier.objects.all()   
#     table = tables.SupplierTable 
#     model_form = forms.SupplierCSVForm


# class SupplierBulkEditView(generic.BulkEditView):
#     queryset = models.Supplier.objects.all()
#     filterset = filtersets.SupplierFilterSet
#     table = tables.SupplierTable
#     form = forms.SupplierBulkEditForm


class SupplierBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Supplier.objects.all()
    table = tables.SupplierTable
