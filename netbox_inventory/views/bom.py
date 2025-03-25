from netbox.views import generic
from tenancy.views import ObjectContactsView
from utilities.query import count_related
from utilities.views import register_model_view

from .. import filtersets, forms, models, tables

__all__ = (
    'BOMView',
    'BOMListView',
    'BOMEditView',
    'BOMDeleteView',
    'BOMBulkImportView',
    'BOMBulkEditView',
    'BOMBulkDeleteView',
    'BOMContactsView',
)


@register_model_view(models.BOM)
class BOMView(generic.ObjectView):
    queryset = models.BOM.objects.all()

    def get_extra_context(self, request, instance):
        return {
            # 'purchase_count': models.Purchase.objects.filter(bom=instance).count(),
            'asset_count': models.Asset.objects.filter(
                bom=instance
            ).count(),
        }


@register_model_view(models.BOM, 'list', path='', detail=False)
class BOMListView(generic.ObjectListView):
    queryset = models.BOM.objects.annotate(
        purchase_count=count_related(models.Purchase, 'supplier'),
        asset_count=count_related(models.Asset, 'bom'),
    )
    table = tables.BOMTable
    filterset = filtersets.BOMFilterSet
    filterset_form = forms.BOMFilterForm


@register_model_view(models.BOM, 'edit')
@register_model_view(models.BOM, 'add', detail=False)
class BOMEditView(generic.ObjectEditView):
    queryset = models.BOM.objects.all()
    form = forms.BOMForm


@register_model_view(models.BOM, 'delete')
class BOMDeleteView(generic.ObjectDeleteView):
    queryset = models.BOM.objects.all()


@register_model_view(models.BOM, 'bulk_import', path='import', detail=False)
class BOMBulkImportView(generic.BulkImportView):
    queryset = models.BOM.objects.all()
    model_form = forms.BOMImportForm


@register_model_view(models.BOM, 'bulk_edit', path='edit', detail=False)
class BOMBulkEditView(generic.BulkEditView):
    queryset = models.BOM.objects.all()
    filterset = filtersets.BOMFilterSet
    table = tables.BOMTable
    form = forms.BOMBulkEditForm


@register_model_view(models.BOM, 'bulk_delete', path='delete', detail=False)
class BOMBulkDeleteView(generic.BulkDeleteView):
    queryset = models.BOM.objects.all()
    table = tables.BOMTable


@register_model_view(models.BOM, 'contacts')
class BOMContactsView(ObjectContactsView):
    queryset = models.BOM.objects.all()
