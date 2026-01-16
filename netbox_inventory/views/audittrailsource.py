from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from .. import filtersets, forms, models, tables

__all__ = (
    'AuditTrailSourceView',
    'AuditTrailSourceListView',
    'AuditTrailSourceEditView',
    'AuditTrailSourceDeleteView',
    'AuditTrailSourceBulkImportView',
    'AuditTrailSourceBulkEditView',
    'AuditTrailSourceBulkDeleteView',
)


@register_model_view(models.AuditTrailSource)
class AuditTrailSourceView(generic.ObjectView):
    queryset = models.AuditTrailSource.objects.all()


@register_model_view(models.AuditTrailSource, 'trails')
class AuditTrailSourceTrailsView(generic.ObjectChildrenView):
    queryset = models.AuditTrailSource.objects.all()
    child_model = models.AuditTrail
    table = tables.AuditTrailTable
    tab = ViewTab(
        label=_('Trails'),
        badge=lambda obj: obj.audit_trails.count(),
        permission='netbox_inventory.view_audittrail',
        weight=1000,
    )

    def get_children(
        self,
        request: HttpRequest,
        parent: models.AuditTrailSource,
    ) -> QuerySet:
        return parent.audit_trails.restrict(request.user, 'view')


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
    'bulk_edit',
    path='edit',
    detail=False
)
class AuditTrailSourceBulkEditView(generic.BulkEditView):
    queryset = models.AuditTrailSource.objects.all()
    filterset = filtersets.AuditTrailSourceFilterSet
    table = tables.AuditTrailSourceTable
    form = forms.AuditTrailSourceBulkEditForm


@register_model_view(
    models.AuditTrailSource,
    'bulk_delete',
    path='delete',
    detail=False,
)
class AuditTrailSourceBulkDeleteView(generic.BulkDeleteView):
    queryset = models.AuditTrailSource.objects.all()
    table = tables.AuditTrailSourceTable
