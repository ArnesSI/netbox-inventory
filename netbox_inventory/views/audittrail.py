from django.contrib import messages
from django.db import transaction
from django.db.models import Model, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.generic import View

from core.models import ObjectType
from netbox.object_actions import BulkDelete, BulkExport, BulkImport
from netbox.views import generic
from utilities.views import (
    ConditionalLoginRequiredMixin,
    GetReturnURLMixin,
    ObjectPermissionRequiredMixin,
    ViewTab,
    register_model_view,
)

from .. import filtersets, forms, models, tables

__all__ = (
    # AuditTrail
    'AuditTrailListView',
    'AuditTrailDeleteView',
    'AuditTrailBulkImportView',
    'AuditTrailBulkDeleteView',
    # Objects
    'ObjectAuditTrailView',
)


#
# AuditTrail
#


@register_model_view(models.AuditTrail, 'list', path='', detail=False)
class AuditTrailListView(generic.ObjectListView):
    queryset = models.AuditTrail.objects.prefetch_related('object_changes__user')
    table = tables.AuditTrailTable
    filterset = filtersets.AuditTrailFilterSet
    filterset_form = forms.AuditTrailFilterForm
    actions = (BulkImport, BulkExport, BulkDelete)


@register_model_view(models.AuditTrail, 'delete')
class AuditTrailDeleteView(generic.ObjectDeleteView):
    queryset = models.AuditTrail.objects.all()


@register_model_view(models.AuditTrail, 'bulk_add', path='bulk-add', detail=False)
class AuditTrailBulkAddView(GetReturnURLMixin, ObjectPermissionRequiredMixin, View):
    queryset = models.AuditTrail.objects.all()

    def get_required_permission(self):
        return 'netbox_inventory.add_audittrail'

    def post(self, request: HttpRequest) -> HttpResponse:
        object_type = get_object_or_404(
            ObjectType,
            pk=request.POST.get('object_type_id'),
        )
        model = object_type.model_class()

        with transaction.atomic():
            count = 0
            for obj in model.objects.filter(
                pk__in=request.POST.getlist('pk'),
            ):
                models.AuditTrail.objects.create(object=obj)
                count += 1

        if count > 0:
            messages.success(
                request,
                _('Marked {count} {type} as seen').format(
                    count=count,
                    type=model._meta.verbose_name_plural,
                ),
            )

        return redirect(self.get_return_url(request))


@register_model_view(models.AuditTrail, 'bulk_import', path='import', detail=False)
class AuditTrailBulkImportView(generic.BulkImportView):
    queryset = models.AuditTrail.objects.all()
    model_form = forms.AuditTrailImportForm


@register_model_view(models.AuditTrail, 'bulk_delete', path='delete', detail=False)
class AuditTrailBulkDeleteView(generic.BulkDeleteView):
    queryset = models.AuditTrail.objects.all()
    table = tables.AuditTrailTable


#
# Objects
#


class ObjectAuditTrailView(ConditionalLoginRequiredMixin, View):
    """
    List audit trails of an object.
    """

    tab = ViewTab(
        label=_('Audit'),
        badge=lambda obj: ObjectAuditTrailView.get_audit_trails(obj).count(),
        permission='netbox_inventory.view_audittrail',
        weight=4000,
        hide_if_empty=True,
    )

    @staticmethod
    def get_audit_trails(obj: Model) -> QuerySet:
        return models.AuditTrail.objects.filter(
            object_type=ObjectType.objects.get_for_model(obj),
            object_id=obj.pk,
        )

    def get(self, request, model, **kwargs) -> HttpResponse:
        # Get parent object and handle QuerySet restriction if needed.
        if hasattr(model.objects, 'restrict'):
            obj = get_object_or_404(
                model.objects.restrict(request.user, 'view'),
                **kwargs,
            )
        else:
            obj = get_object_or_404(model, **kwargs)

        # Prepare table for listing all audit trails of this object.
        table = tables.AuditTrailTable(
            data=self.get_audit_trails(obj).prefetch_related('object_changes__user'),
            user=request.user,
        )
        table.configure(request)

        return render(
            request,
            'generic/object_children.html',
            {
                'object': obj,
                'model': model,
                'child_model': models.AuditTrail,
                'base_template': f'{model._meta.app_label}/{model._meta.model_name}.html',
                'table': table,
                'table_config': f'{table.name}_config',
                'tab': self.tab,
                'return_url': request.get_full_path(),
            },
        )
