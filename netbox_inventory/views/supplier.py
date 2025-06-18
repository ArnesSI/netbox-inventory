from netbox.views import generic
from utilities.query import count_related
from utilities.views import register_model_view

from .. import filtersets, forms, models, tables

__all__ = (
    'SupplierView',
    'SupplierListView',
    'SupplierEditView',
    'SupplierDeleteView',
    'SupplierBulkImportView',
    'SupplierBulkEditView',
    'SupplierBulkDeleteView',
)


@register_model_view(models.Supplier)
class SupplierView(generic.ObjectView):
    queryset = models.Supplier.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'asset_count': models.Asset.objects.filter(
                purchase__supplier=instance
            ).count(),
            'purchase_count': models.Purchase.objects.filter(supplier=instance).count(),
            'delivery_count': models.Delivery.objects.filter(
                purchase__supplier=instance
            ).count(),
        }


@register_model_view(models.Supplier, 'list', path='', detail=False)
class SupplierListView(generic.ObjectListView):
    queryset = models.Supplier.objects.annotate(
        purchase_count=count_related(models.Purchase, 'supplier'),
        delivery_count=count_related(models.Delivery, 'purchase__supplier'),
        asset_count=count_related(models.Asset, 'purchase__supplier'),
    )
    table = tables.SupplierTable
    filterset = filtersets.SupplierFilterSet
    filterset_form = forms.SupplierFilterForm


@register_model_view(models.Supplier, 'edit')
@register_model_view(models.Supplier, 'add', detail=False)
class SupplierEditView(generic.ObjectEditView):
    queryset = models.Supplier.objects.all()
    form = forms.SupplierForm


@register_model_view(models.Supplier, 'delete')
class SupplierDeleteView(generic.ObjectDeleteView):
    queryset = models.Supplier.objects.all()


@register_model_view(models.Supplier, 'bulk_import', path='import', detail=False)
class SupplierBulkImportView(generic.BulkImportView):
    queryset = models.Supplier.objects.all()
    model_form = forms.SupplierImportForm


@register_model_view(models.Supplier, 'bulk_edit', path='edit', detail=False)
class SupplierBulkEditView(generic.BulkEditView):
    queryset = models.Supplier.objects.all()
    filterset = filtersets.SupplierFilterSet
    table = tables.SupplierTable
    form = forms.SupplierBulkEditForm


@register_model_view(models.Supplier, 'bulk_delete', path='delete', detail=False)
class SupplierBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Supplier.objects.all()
    filterset = filtersets.SupplierFilterSet
    table = tables.SupplierTable
