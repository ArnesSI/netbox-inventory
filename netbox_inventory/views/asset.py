from django.db import IntegrityError
from django.template import Template

from netbox.views import generic
from utilities.views import register_model_view

from .. import filtersets, forms, models, tables
from ..template_content import WARRANTY_PROGRESSBAR

__all__ = (
    'AssetView',
    'AssetListView',
    'AssetBulkCreateView',
    'AssetEditView',
    'AssetDeleteView',
    'AssetBulkImportView',
    'AssetBulkEditView',
    'AssetBulkDeleteView',
)


@register_model_view(models.Asset)
class AssetView(generic.ObjectView):
    queryset = models.Asset.objects.all()

    def get_extra_context(self, request, instance):
        context = super().get_extra_context(request, instance)
        context['warranty_progressbar'] = Template(WARRANTY_PROGRESSBAR)
        return context


@register_model_view(models.Asset, 'list', path='', detail=False)
class AssetListView(generic.ObjectListView):
    queryset = models.Asset.objects.prefetch_related(
        'device_type__manufacturer',
        'module_type__manufacturer',
        'inventoryitem_type__manufacturer',
        'rack_type__manufacturer',
        'device__role',
        'module__module_bay',
        'module__module_type',
        'inventoryitem__role',
        'rack__role',
        'owning_tenant',
        'purchase__supplier',
        'delivery',
        'storage_location',
    )
    table = tables.AssetTable
    filterset = filtersets.AssetFilterSet
    filterset_form = forms.AssetFilterForm


@register_model_view(models.Asset, 'bulk_add', path='bulk-add', detail=False)
class AssetBulkCreateView(generic.BulkCreateView):
    queryset = models.Asset.objects.all()
    form = forms.AssetBulkAddForm
    model_form = forms.AssetBulkAddModelForm
    pattern_target = None
    template_name = 'netbox_inventory/asset_bulk_add.html'

    def _create_objects(self, form, request):
        new_objects = []
        for _ in range(form.cleaned_data['count']):
            # Reinstantiate the model form each time to avoid overwriting the same instance. Use a mutable
            # copy of the POST QueryDict so that we can update the target field value.
            model_form = self.model_form(request.POST.copy())
            del model_form.data['count']

            # Validate each new object independently.
            if model_form.is_valid():
                obj = model_form.save()
                new_objects.append(obj)
            else:
                # Raise an IntegrityError to break the for loop and abort the transaction.
                raise IntegrityError()

        return new_objects


@register_model_view(models.Asset, 'edit')
@register_model_view(models.Asset, 'add', detail=False)
class AssetEditView(generic.ObjectEditView):
    queryset = models.Asset.objects.all()
    form = forms.AssetForm
    template_name = 'netbox_inventory/asset_edit.html'


@register_model_view(models.Asset, 'delete')
class AssetDeleteView(generic.ObjectDeleteView):
    queryset = models.Asset.objects.all()


@register_model_view(models.Asset, 'bulk_import', path='import', detail=False)
class AssetBulkImportView(generic.BulkImportView):
    queryset = models.Asset.objects.all()
    model_form = forms.AssetImportForm
    template_name = 'netbox_inventory/asset_bulk_import.html'


@register_model_view(models.Asset, 'bulk_edit', path='edit', detail=False)
class AssetBulkEditView(generic.BulkEditView):
    queryset = models.Asset.objects.all()
    filterset = filtersets.AssetFilterSet
    table = tables.AssetTable
    form = forms.AssetBulkEditForm


@register_model_view(models.Asset, 'bulk_delete', path='delete', detail=False)
class AssetBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Asset.objects.all()
    filterset = filtersets.AssetFilterSet
    table = tables.AssetTable
