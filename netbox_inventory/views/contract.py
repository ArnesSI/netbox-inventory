from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ..filtersets import ContractFilterSet
from ..forms import ContractForm
from ..models import Contract
from ..tables import ContractTable


class ContractListView(generic.ObjectListView):
    queryset = Contract.objects.all()
    table = ContractTable
    filterset = ContractFilterSet
    filterset_form = ContractForm


class ContractView(generic.ObjectView):
    queryset = Contract.objects.all()

    def get_extra_context(self, request, instance):
        # Get related assets
        related_assets = instance.assets.all()
        
        return {
            'related_assets': related_assets,
        }


class ContractEditView(generic.ObjectEditView):
    queryset = Contract.objects.all()
    form = ContractForm


class ContractDeleteView(generic.ObjectDeleteView):
    queryset = Contract.objects.all()


class ContractBulkImportView(generic.BulkImportView):
    queryset = Contract.objects.all()
    model_form = ContractForm


class ContractBulkEditView(generic.BulkEditView):
    queryset = Contract.objects.all()
    filterset = ContractFilterSet
    table = ContractTable
    form = ContractForm


class ContractBulkDeleteView(generic.BulkDeleteView):
    queryset = Contract.objects.all()
    filterset = ContractFilterSet
    table = ContractTable


# Register model views
register_model_view(Contract, 'list', ContractListView, 'contracts')
register_model_view(Contract, 'add', ContractEditView)
register_model_view(Contract, 'edit', ContractEditView)
register_model_view(Contract, 'delete', ContractDeleteView)
register_model_view(Contract, 'bulk_import', ContractBulkImportView)
register_model_view(Contract, 'bulk_edit', ContractBulkEditView)
register_model_view(Contract, 'bulk_delete', ContractBulkDeleteView) 