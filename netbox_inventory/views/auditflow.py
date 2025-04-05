from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from .. import filtersets, forms, models, tables

__all__ = (
    'AuditFlowAssignedPagesView',
    'AuditFlowView',
    'AuditFlowListView',
    'AuditFlowEditView',
    'AuditFlowDeleteView',
    'AuditFlowBulkImportView',
    'AuditFlowBulkEditView',
    'AuditFlowBulkDeleteView',
)


@register_model_view(models.AuditFlow)
class AuditFlowView(generic.ObjectView):
    queryset = models.AuditFlow.objects.all()


@register_model_view(models.AuditFlow, 'pages')
class AuditFlowAssignedPagesView(generic.ObjectChildrenView):
    queryset = models.AuditFlow.objects.all()
    child_model = models.AuditFlowPageAssignment
    table = tables.AuditFlowPageAssignmentTable
    template_name = 'netbox_inventory/auditflow_pages.html'
    tab = ViewTab(
        label=_('Pages'),
        badge=lambda obj: obj.pages.count(),
        permission='netbox_inventory.view_auditflowpage',
        weight=1000,
    )

    def get_children(self, request: HttpRequest, parent: models.AuditFlow) -> QuerySet:
        return parent.assigned_pages.restrict(request.user, 'view')

    def get_table(self, *args, **kwargs):
        table = super().get_table(*args, **kwargs)
        table.columns.hide('flow')
        return table


@register_model_view(models.AuditFlow, 'list', path='', detail=False)
class AuditFlowListView(generic.ObjectListView):
    queryset = models.AuditFlow.objects.all()
    table = tables.AuditFlowTable
    filterset = filtersets.AuditFlowFilterSet
    filterset_form = forms.AuditFlowFilterForm


@register_model_view(models.AuditFlow, 'add', detail=False)
@register_model_view(models.AuditFlow, 'edit')
class AuditFlowEditView(generic.ObjectEditView):
    queryset = models.AuditFlow.objects.all()
    form = forms.AuditFlowForm


@register_model_view(models.AuditFlow, 'delete')
class AuditFlowDeleteView(generic.ObjectDeleteView):
    queryset = models.AuditFlow.objects.all()


@register_model_view(models.AuditFlow, 'bulk_import', path='import', detail=False)
class AuditFlowBulkImportView(generic.BulkImportView):
    queryset = models.AuditFlow.objects.all()
    model_form = forms.AuditFlowImportForm


@register_model_view(models.AuditFlow, 'bulk_edit', path='edit', detail=False)
class AuditFlowBulkEditView(generic.BulkEditView):
    queryset = models.AuditFlow.objects.all()
    filterset = filtersets.AuditFlowFilterSet
    table = tables.AuditFlowTable
    form = forms.AuditFlowBulkEditForm


@register_model_view(models.AuditFlow, 'bulk_delete', path='delete', detail=False)
class AuditFlowBulkDeleteView(generic.BulkDeleteView):
    queryset = models.AuditFlow.objects.all()
    table = tables.AuditFlowTable
