from netbox.views import generic
from utilities.views import register_model_view

from .. import filtersets, forms, models, tables

__all__ = (
    'AuditTrailSourceView',
    'AuditTrailSourceListView',
    'AuditTrailSourceEditView',
    'AuditTrailSourceDeleteView',
    'AuditTrailSourceBulkImportView',
    'AuditTrailSourceBulkDeleteView',
)


@register_model_view(models.AuditTrailSource)
class AuditTrailSourceView(generic.ObjectView):
    queryset = models.AuditTrailSource.objects.all()


@register_model_view(models.AuditTrailSource, 'list', path='', detail=False)
class AuditTrailSourceListView(generic.ObjectListView):
    queryset = models.AuditTrailSource.objects.all()
    table = tables.AuditTrailSourceTable
    filterset = filtersets.AuditTrailSourceFilterSet
    filterset_form = forms.AuditTrailSourceFilterForm


@register_model_view(models.AuditTrailSource, 'add', detail=False)
@register_model_view(models.AuditTrailSource, 'edit')
class AuditTrailSourceEditView(generic.ObjectEditView):
    queryset = models.AuditTrailSource.objects.all()
    form = forms.AuditTrailSourceForm


@register_model_view(models.AuditTrailSource, 'delete')
class AuditTrailSourceDeleteView(generic.ObjectDeleteView):
    queryset = models.AuditTrailSource.objects.all()


@register_model_view(
    models.AuditTrailSource,
    'bulk_import',
    path='import',
    detail=False,
)
class AuditTrailSourceBulkImportView(generic.BulkImportView):
    queryset = models.AuditTrailSource.objects.all()
    model_form = forms.AuditTrailSourceImportForm


@register_model_view(
    models.AuditTrailSource,
    'bulk_delete',
    path='delete',
    detail=False,
)
class AuditTrailSourceBulkDeleteView(generic.BulkDeleteView):
    queryset = models.AuditTrailSource.objects.all()
    table = tables.AuditTrailSourceTable
