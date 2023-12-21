from netbox.views import generic
from utilities.utils import count_related
from .. import filtersets, forms, models, tables

__all__ = (
    'ConsumableView',
    'ConsumableListView',
    'ConsumableEditView',
    'ConsumableDeleteView',
    'ConsumableBulkImportView',
    'ConsumableBulkEditView',
    'ConsumableBulkDeleteView',
)

class ConsumableView(generic.ObjectView):
    queryset = models.Consumable.objects.all()


class ConsumableListView(generic.ObjectListView):
    queryset = models.Consumable.objects.all()
    table = tables.ConsumableTable
    filterset = filtersets.ConsumableFilterSet
    filterset_form = forms.ConsumableFilterForm


class ConsumableEditView(generic.ObjectEditView):
    queryset = models.Consumable.objects.all()
    form = forms.ConsumableForm


class ConsumableDeleteView(generic.ObjectDeleteView):
    queryset = models.Consumable.objects.all()


class ConsumableBulkImportView(generic.BulkImportView):
    queryset = models.Consumable.objects.all()
    model_form = forms.ConsumableImportForm


class ConsumableBulkEditView(generic.BulkEditView):
    queryset = models.Consumable.objects.all()
    filterset = filtersets.ConsumableFilterSet
    table = tables.ConsumableTable
    form = forms.ConsumableBulkEditForm


class ConsumableBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Consumable.objects.all()
    table = tables.ConsumableTable
