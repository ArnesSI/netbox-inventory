from netbox.views import generic
from utilities.views import register_model_view

from .. import forms, models, tables

__all__ = (
    'AuditFlowPageAssignmentEditView',
    'AuditFlowPageAssignmentDeleteView',
    'AuditFlowPageAssignmentBulkEditView',
    'AuditFlowPageAssignmentBulkDeleteView',
)


@register_model_view(models.AuditFlowPageAssignment, 'add', detail=False)
@register_model_view(models.AuditFlowPageAssignment, 'edit')
class AuditFlowPageAssignmentEditView(generic.ObjectEditView):
    queryset = models.AuditFlowPageAssignment.objects.all()
    form = forms.AuditFlowPageAssignmentForm


@register_model_view(models.AuditFlowPageAssignment, 'delete')
class AuditFlowPageAssignmentDeleteView(generic.ObjectDeleteView):
    queryset = models.AuditFlowPageAssignment.objects.all()


@register_model_view(
    models.AuditFlowPageAssignment,
    'bulk_edit',
    path='edit',
    detail=False,
)
class AuditFlowPageAssignmentBulkEditView(generic.BulkEditView):
    queryset = models.AuditFlowPageAssignment.objects.all()
    table = tables.AuditFlowPageAssignmentTable
    form = forms.AuditFlowPageAssignmentBulkEditForm


@register_model_view(
    models.AuditFlowPageAssignment,
    'bulk_delete',
    path='delete',
    detail=False,
)
class AuditFlowPageAssignmentBulkDeleteView(generic.BulkDeleteView):
    queryset = models.AuditFlowPageAssignment.objects.all()
    table = tables.AuditFlowPageAssignmentTable
