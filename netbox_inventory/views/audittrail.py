from netbox.views import generic
from utilities.views import register_model_view

from .. import filtersets, forms, models, tables

__all__ = (
    'AuditTrailListView',
    'AuditTrailDeleteView',
    'AuditTrailBulkImportView',
    'AuditTrailBulkDeleteView',
)


@register_model_view(models.AuditTrail, 'list', path='', detail=False)
class AuditTrailListView(generic.ObjectListView):
    queryset = models.AuditTrail.objects.all()
    table = tables.AuditTrailTable
    filterset = filtersets.AuditTrailFilterSet
    filterset_form = forms.AuditTrailFilterForm


@register_model_view(models.AuditTrail, 'delete')
class AuditTrailDeleteView(generic.ObjectDeleteView):
    queryset = models.AuditTrail.objects.all()


@register_model_view(models.AuditTrail, 'bulk_import', path='import', detail=False)
class AuditTrailBulkImportView(generic.BulkImportView):
    queryset = models.AuditTrail.objects.all()
    model_form = forms.AuditTrailImportForm


@register_model_view(models.AuditTrail, 'bulk_delete', path='delete', detail=False)
class AuditTrailBulkDeleteView(generic.BulkDeleteView):
    queryset = models.AuditTrail.objects.all()
    table = tables.AuditTrailTable
