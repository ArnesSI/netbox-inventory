from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ..filtersets import ContractFilterSet
from ..forms import ContractForm, ContractFilterForm
from ..models import Contract
from ..tables import ContractTable

__all__ = (
    'ContractView',
    'ContractListView',
    'ContractEditView',
    'ContractDeleteView',
    'ContractBulkImportView',
    'ContractBulkEditView',
    'ContractBulkDeleteView',
)


@register_model_view(Contract)
class ContractView(generic.ObjectView):
    queryset = Contract.objects.all()

    def get_extra_context(self, request, instance):
        # Get related assets
        related_assets = instance.assets.all()
        
        return {
            'related_assets': related_assets,
        }


@register_model_view(Contract, 'list', path='', detail=False)
class ContractListView(generic.ObjectListView):
    queryset = Contract.objects.all()
    table = ContractTable
    filterset = ContractFilterSet
    filterset_form = ContractFilterForm


@register_model_view(Contract, 'edit')
@register_model_view(Contract, 'add', detail=False)
class ContractEditView(generic.ObjectEditView):
    queryset = Contract.objects.all()
    form = ContractForm


@register_model_view(Contract, 'delete')
class ContractDeleteView(generic.ObjectDeleteView):
    queryset = Contract.objects.all()


@register_model_view(Contract, 'bulk_import', path='import', detail=False)
class ContractBulkImportView(generic.BulkImportView):
    queryset = Contract.objects.all()
    model_form = ContractForm


@register_model_view(Contract, 'bulk_edit', path='edit', detail=False)
class ContractBulkEditView(generic.BulkEditView):
    queryset = Contract.objects.all()
    filterset = ContractFilterSet
    table = ContractTable
    form = ContractForm


@register_model_view(Contract, 'bulk_delete', path='delete', detail=False)
class ContractBulkDeleteView(generic.BulkDeleteView):
    queryset = Contract.objects.all()
    filterset = ContractFilterSet
    table = ContractTable