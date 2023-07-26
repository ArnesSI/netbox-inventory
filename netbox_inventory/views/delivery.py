from netbox.views import generic
from utilities.utils import count_related
from .. import filtersets, forms, models, tables

__all__ = (
    'DeliveryView',
    'DeliveryListView',
    'DeliveryEditView',
    'DeliveryDeleteView',
    'DeliveryBulkImportView',
    'DeliveryBulkEditView',
    'DeliveryBulkDeleteView',
)

class DeliveryView(generic.ObjectView):
    queryset = models.Delivery.objects.all()

    def get_extra_context(self, request, instance):
        delivery_assets = models.Asset.objects.restrict(request.user, 'view').filter(
            delivery=instance
        )
        asset_table = tables.AssetTable(delivery_assets, user=request.user)
        asset_table.columns.hide('delivery')
        asset_table.columns.hide('delivery_date')
        asset_table.columns.hide('purchase')
        asset_table.columns.hide('purchase_date')
        asset_table.columns.hide('supplier')
        asset_table.configure(request)

        return {
            'asset_table': asset_table,
            'asset_count': models.Asset.objects.filter(delivery=instance).count(),
        }


class DeliveryListView(generic.ObjectListView):
    queryset = models.Delivery.objects.annotate(
        asset_count=count_related(models.Asset, 'delivery'),
    )
    table = tables.DeliveryTable
    filterset = filtersets.DeliveryFilterSet
    filterset_form = forms.DeliveryFilterForm


class DeliveryEditView(generic.ObjectEditView):
    queryset = models.Delivery.objects.all()
    form = forms.DeliveryForm


class DeliveryDeleteView(generic.ObjectDeleteView):
    queryset = models.Delivery.objects.all()


class DeliveryBulkImportView(generic.BulkImportView):
    queryset = models.Delivery.objects.all()
    model_form = forms.DeliveryImportForm


class DeliveryBulkEditView(generic.BulkEditView):
    queryset = models.Delivery.objects.all()
    filterset = filtersets.DeliveryFilterSet
    table = tables.DeliveryTable
    form = forms.DeliveryBulkEditForm


class DeliveryBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Delivery.objects.all()
    table = tables.DeliveryTable
