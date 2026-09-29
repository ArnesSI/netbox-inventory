from django.db import IntegrityError
from django.template import Template
from django.utils.translation import gettext as _

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
        pattern_values = form.cleaned_data.get('pattern')

        if pattern_values:
            return self._create_objects_by_tag_pattern(form, request, pattern_values)

        return self._create_objects_by_count(form, request, form.cleaned_data['count'])

    def _add_model_form_errors(self, form, model_form, value, pattern_field=None):
        """
        Copy validation errors from a single generated object's model form back onto
        the outer bulk-add form so they are shown to the user, instead of being
        silently discarded (#298). ``pattern_field``, if given, is bound to the
        'pattern' input instead of listed generically, mirroring how the base
        BulkCreateView.add_model_form_errors() treats its own pattern_target.
        """
        errors = model_form.errors.as_data()

        if pattern_field and errors.get(pattern_field):
            form.add_error('pattern', errors.pop(pattern_field))

        for field_name, field_errors in errors.items():
            if field_name == '__all__':
                field_label = _('General')
            elif field_name in model_form.fields:
                field_label = model_form.fields[field_name].label
            else:
                field_label = field_name

            for error in field_errors:
                for message in error.messages:
                    form.add_error(
                        None,
                        _('{value}: {field}: {error}').format(
                            value=value, field=field_label, error=message,
                        )
                    )

    def _create_objects_by_count(self, form, request, count):
        new_objects = []
        for i in range(count):
            # Reinstantiate the model form each time to avoid overwriting the same instance. Use a mutable
            # copy of the POST QueryDict so that we can update the target field value.
            model_form = self.model_form(request.POST.copy())
            del model_form.data['count']
            model_form.data.pop('pattern', None)

            # Validate each new object independently.
            if model_form.is_valid():
                obj = model_form.save()
                new_objects.append(obj)
            else:
                self._add_model_form_errors(form, model_form, i + 1)
                # Raise an IntegrityError to break the for loop and abort the transaction.
                raise IntegrityError()

        return new_objects

    def _create_objects_by_tag_pattern(self, form, request, pattern_values):
        new_objects = []
        for value in pattern_values:
            model_form = self.model_form(request.POST.copy())
            del model_form.data['count']
            model_form.data.pop('pattern', None)
            # Asset tag is disabled in the bulk-add UI; enable it here so pattern values can be validated & saved.
            model_form.fields['asset_tag'].disabled = False
            model_form.data['asset_tag'] = value

            if model_form.is_valid():
                obj = model_form.save()
                new_objects.append(obj)
            else:
                self._add_model_form_errors(form, model_form, value, pattern_field='asset_tag')
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
