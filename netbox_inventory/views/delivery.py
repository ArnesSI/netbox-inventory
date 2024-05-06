from netbox.views import generic
from utilities.query import count_related
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
        return {
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
