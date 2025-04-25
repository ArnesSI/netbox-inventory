from django.contrib import messages
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import View

from core.models import ObjectType
from netbox.views import generic
from utilities.views import (
    GetReturnURLMixin,
    ObjectPermissionRequiredMixin,
    register_model_view,
)

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
