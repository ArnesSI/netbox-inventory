from netbox.views import generic
from utilities.query import count_related
from utilities.views import register_model_view

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


@register_model_view(models.Delivery)
class DeliveryView(generic.ObjectView):
    queryset = models.Delivery.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'asset_count': models.Asset.objects.filter(delivery=instance).count(),
        }


@register_model_view(models.Delivery, 'list', path='', detail=False)
class DeliveryListView(generic.ObjectListView):
    queryset = models.Delivery.objects.annotate(
        asset_count=count_related(models.Asset, 'delivery'),
    )
    table = tables.DeliveryTable
    filterset = filtersets.DeliveryFilterSet
    filterset_form = forms.DeliveryFilterForm


@register_model_view(models.Delivery, 'edit')
@register_model_view(models.Delivery, 'add', detail=False)
class DeliveryEditView(generic.ObjectEditView):
    queryset = models.Delivery.objects.all()
    form = forms.DeliveryForm


@register_model_view(models.Delivery, 'delete')
class DeliveryDeleteView(generic.ObjectDeleteView):
    queryset = models.Delivery.objects.all()


@register_model_view(models.Delivery, 'bulk_import', path='import', detail=False)
class DeliveryBulkImportView(generic.BulkImportView):
    queryset = models.Delivery.objects.all()
    model_form = forms.DeliveryImportForm


@register_model_view(models.Delivery, 'bulk_edit', path='edit', detail=False)
class DeliveryBulkEditView(generic.BulkEditView):
    queryset = models.Delivery.objects.all()
    filterset = filtersets.DeliveryFilterSet
    table = tables.DeliveryTable
    form = forms.DeliveryBulkEditForm


@register_model_view(models.Delivery, 'bulk_delete', path='delete', detail=False)
class DeliveryBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Delivery.objects.all()
    filterset = filtersets.DeliveryFilterSet
    table = tables.DeliveryTable
