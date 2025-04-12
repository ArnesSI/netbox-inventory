from django.core.exceptions import PermissionDenied
from django.db.models import Model, QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import resolve, reverse
from django.utils.translation import gettext_lazy as _

from netbox.views import generic
from utilities.views import ViewTab, get_viewname, register_model_view

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
    'AuditFlowRunView',
)


#
# Admin
#


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


#
# Run
#


@register_model_view(models.AuditFlow, 'run')
class AuditFlowRunView(generic.ObjectChildrenView):
    """
    Run an `AuditFlow` for a specific start object (e.g. a specific `Location`).
    """

    queryset = models.AuditFlow.objects.all()
    template_name = 'netbox_inventory/auditflow_run.html'

    def get_required_permission(self):
        return 'netbox_inventory.run_auditflow'

    @staticmethod
    def get_current_page(
        request: HttpRequest,
        parent: models.AuditFlow,
    ) -> models.AuditFlowPageAssignment:
        """
        Get the currently selected `AuditFlowPage` of the `AuditFlow` based on the `tab`
        query parameter. Defaults to the first assigned page.
        """
        assignment_id = request.GET.get('tab')
        if assignment_id:
            return get_object_or_404(parent.assigned_pages, pk=assignment_id)
        return parent.assigned_pages.first()

    @staticmethod
    def get_object_or_raise(
        queryset: QuerySet,
        request: HttpRequest,
        **kwargs,
    ) -> Model:
        """
        Get an object from `queryset` and raise exceptions either if the object can't be
        found or if the `request` user doesn't have permissions to view the object.
        """
        obj = get_object_or_404(queryset, **kwargs)
        if not queryset.restrict(request.user, 'view').contains(obj):
            raise PermissionDenied()
        return obj

    def get_children(self, request: HttpRequest, parent: models.AuditFlow) -> QuerySet:
        # Each AuditFlowPage handles one specific object type. To support different
        # types of objects with this view, dynamically retrieve the object type model
        # and set class properties for use in other methods and templates.
        page = self.get_current_page(request, parent)
        self.tab = page.pk
        self.child_model = page.page.object_type.model_class()

        # Attributes related to displaying the list of child objects are copied from the
        # object's list view. This allows reusing the existing logic and displaying the
        # objects with the preferences defined by the user.
        view = resolve(reverse(get_viewname(self.child_model, 'list'))).func.view_class
        self.table = getattr(view, 'table', None)
        self.filterset = getattr(view, 'filterset', None)

        # Get the flow start object (e.g. a Site or Location) and limit the page object
        # queryset to that limited audit location.
        self.start_object = self.get_object_or_raise(
            parent.get_objects(),
            request,
            pk=request.GET.get('object_id'),
        )
        return page.get_objects(self.start_object)

    def get_extra_context(self, request: HttpRequest, parent: models.AuditFlow) -> dict:
        return {
            'flow_pages': parent.assigned_pages.all(),
            'start_object': self.start_object,
        }
