from netbox.views import generic
from utilities.query import count_related
from utilities.views import register_model_view

from .. import filtersets, forms, models, tables

__all__ = (
    'TransferView',
    'TransferListView',
    'TransferEditView',
    'TransferDeleteView',
    'TransferBulkImportView',
    'TransferBulkEditView',
    'TransferBulkDeleteView',
)


@register_model_view(models.Transfer)
class TransferView(generic.ObjectView):
    queryset = models.Transfer.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'asset_count': models.Asset.objects.filter(transfer=instance).count(),
        }


@register_model_view(models.Transfer, 'list', path='', detail=False)
class TransferListView(generic.ObjectListView):
    queryset = models.Transfer.objects.annotate(
        asset_count=count_related(models.Asset, 'transfer'),
    )
    table = tables.TransferTable
    filterset = filtersets.TransferFilterSet
    filterset_form = forms.TransferFilterForm


@register_model_view(models.Transfer, 'edit')
@register_model_view(models.Transfer, 'add', detail=False)
class TransferEditView(generic.ObjectEditView):
    queryset = models.Transfer.objects.all()
    form = forms.TransferForm


@register_model_view(models.Transfer, 'delete')
class TransferDeleteView(generic.ObjectDeleteView):
    queryset = models.Transfer.objects.all()


@register_model_view(models.Transfer, 'bulk_import', path='import', detail=False)
class TransferBulkImportView(generic.BulkImportView):
    queryset = models.Transfer.objects.all()
    model_form = forms.TransferImportForm


@register_model_view(models.Transfer, 'bulk_edit', path='edit', detail=False)
class TransferBulkEditView(generic.BulkEditView):
    queryset = models.Transfer.objects.all()
    filterset = filtersets.TransferFilterSet
    table = tables.TransferTable
    form = forms.TransferBulkEditForm


@register_model_view(models.Transfer, 'bulk_delete', path='delete', detail=False)
class TransferBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Transfer.objects.all()
    table = tables.TransferTable
