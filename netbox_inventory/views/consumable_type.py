from netbox.views import generic
from utilities.utils import count_related
from .. import filtersets, forms, models, tables

__all__ = (
    'ConsumableTypeView',
    'ConsumableTypeListView',
    'ConsumableTypeEditView',
    'ConsumableTypeDeleteView',
    'ConsumableTypeBulkImportView',
    'ConsumableTypeBulkEditView',
    'ConsumableTypeBulkDeleteView',
)

class ConsumableTypeView(generic.ObjectView):
    queryset = models.ConsumableType.objects.all()


class ConsumableTypeListView(generic.ObjectListView):
    queryset = models.ConsumableType.objects.all()
    table = tables.ConsumableTypeTable
    filterset = filtersets.ConsumableTypeFilterSet
    filterset_form = forms.ConsumableTypeFilterForm


class ConsumableTypeEditView(generic.ObjectEditView):
    queryset = models.ConsumableType.objects.all()
    form = forms.ConsumableTypeForm


class ConsumableTypeDeleteView(generic.ObjectDeleteView):
    queryset = models.ConsumableType.objects.all()


class ConsumableTypeBulkImportView(generic.BulkImportView):
    queryset = models.ConsumableType.objects.all()
    model_form = forms.ConsumableTypeImportForm


class ConsumableTypeBulkEditView(generic.BulkEditView):
    queryset = models.ConsumableType.objects.all()
    filterset = filtersets.ConsumableTypeFilterSet
    table = tables.ConsumableTypeTable
    form = forms.ConsumableTypeBulkEditForm


class ConsumableTypeBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ConsumableType.objects.all()
    table = tables.ConsumableTypeTable
