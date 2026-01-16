from netbox.views import generic
from utilities.views import register_model_view

from .. import filtersets, forms, models, tables

__all__ = (
    'AuditFlowPageView',
    'AuditFlowPageListView',
    'AuditFlowPageEditView',
    'AuditFlowPageDeleteView',
    'AuditFlowPageBulkImportView',
    'AuditFlowPageBulkEditView',
    'AuditFlowPageBulkDeleteView',
)


@register_model_view(models.AuditFlowPage)
class AuditFlowPageView(generic.ObjectView):
    queryset = models.AuditFlowPage.objects.all()


@register_model_view(models.AuditFlowPage, 'list', path='', detail=False)
class AuditFlowPageListView(generic.ObjectListView):
    queryset = models.AuditFlowPage.objects.all()
    table = tables.AuditFlowPageTable
    filterset = filtersets.AuditFlowPageFilterSet
    filterset_form = forms.AuditFlowPageFilterForm


@register_model_view(models.AuditFlowPage, 'add', detail=False)
@register_model_view(models.AuditFlowPage, 'edit')
class AuditFlowPageEditView(generic.ObjectEditView):
    queryset = models.AuditFlowPage.objects.all()
    form = forms.AuditFlowPageForm


@register_model_view(models.AuditFlowPage, 'delete')
class AuditFlowPageDeleteView(generic.ObjectDeleteView):
    queryset = models.AuditFlowPage.objects.all()


@register_model_view(models.AuditFlowPage, 'bulk_import', path='import', detail=False)
class AuditFlowPageBulkImportView(generic.BulkImportView):
    queryset = models.AuditFlowPage.objects.all()
    model_form = forms.AuditFlowPageImportForm


@register_model_view(models.AuditFlowPage, 'bulk_edit', path='edit', detail=False)
class AuditFlowPageBulkEditView(generic.BulkEditView):
    queryset = models.AuditFlowPage.objects.all()
    filterset = filtersets.AuditFlowPageFilterSet
    table = tables.AuditFlowPageTable
    form = forms.AuditFlowPageBulkEditForm


@register_model_view(models.AuditFlowPage, 'bulk_delete', path='delete', detail=False)
class AuditFlowPageBulkDeleteView(generic.BulkDeleteView):
    queryset = models.AuditFlowPage.objects.all()
    table = tables.AuditFlowPageTable
