from netbox.views import generic
from tenancy.views import ObjectContactsView
from utilities.query import count_related
from utilities.views import register_model_view

from .. import filtersets, forms, models, tables

__all__ = (
    'CourierView',
    'CourierListView',
    'CourierEditView',
    'CourierDeleteView',
    'CourierBulkImportView',
    'CourierBulkEditView',
    'CourierBulkDeleteView',
    'CourierContactsView',
)


@register_model_view(models.Courier)
class CourierView(generic.ObjectView):
    queryset = models.Courier.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'transfer_count': models.Transfer.objects.filter(
                courier=instance
            ).count(),
        }


@register_model_view(models.Courier, 'list', path='', detail=False)
class CourierListView(generic.ObjectListView):
    queryset = models.Courier.objects.annotate(
        transfer_count=count_related(models.Transfer, 'courier'),
    )
    table = tables.CourierTable
    filterset = filtersets.CourierFilterSet
    filterset_form = forms.CourierFilterForm


@register_model_view(models.Courier, 'edit')
@register_model_view(models.Courier, 'add', detail=False)
class CourierEditView(generic.ObjectEditView):
    queryset = models.Courier.objects.all()
    form = forms.CourierForm


@register_model_view(models.Courier, 'delete')
class CourierDeleteView(generic.ObjectDeleteView):
    queryset = models.Courier.objects.all()


@register_model_view(models.Courier, 'bulk_import', path='import', detail=False)
class CourierBulkImportView(generic.BulkImportView):
    queryset = models.Courier.objects.all()
    model_form = forms.CourierImportForm


@register_model_view(models.Courier, 'bulk_edit', path='edit', detail=False)
class CourierBulkEditView(generic.BulkEditView):
    queryset = models.Courier.objects.all()
    filterset = filtersets.CourierFilterSet
    table = tables.CourierTable
    form = forms.CourierBulkEditForm


@register_model_view(models.Courier, 'bulk_delete', path='delete', detail=False)
class CourierBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Courier.objects.all()
    table = tables.CourierTable


@register_model_view(models.Courier, 'contacts')
class CourierContactsView(ObjectContactsView):
    queryset = models.Courier.objects.all()
