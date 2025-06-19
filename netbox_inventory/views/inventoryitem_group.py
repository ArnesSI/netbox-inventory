from itertools import groupby

from netbox.views import generic
from utilities.views import register_model_view

from .. import filtersets, forms, models, tables
from ..analyzers import asset_counts_status, asset_counts_type_status

__all__ = (
    'InventoryItemGroupView',
    'InventoryItemGroupListView',
    'InventoryItemGroupEditView',
    'InventoryItemGroupDeleteView',
    'InventoryItemGroupBulkImportView',
    'InventoryItemGroupBulkEditView',
    'InventoryItemGroupBulkDeleteView',
)


@register_model_view(models.InventoryItemGroup)
class InventoryItemGroupView(generic.ObjectView):
    queryset = models.InventoryItemGroup.objects.all()

    def get_extra_context(self, request, instance):
        # get assets from this and all child groups
        assets = (
            models.Asset.objects.filter(
                inventoryitem_groups__in=instance.get_descendants(include_self=True)
            )
            .distinct()
            .prefetch_related('inventoryitem_groups')
            .select_related(
                'device_type', 'module_type', 'rack_type', 'inventoryitem_type'
            )
        )
        # get counts for each type and status combination
        type_status_counts = asset_counts_type_status(assets, instance)

        # group by hw type keys with all statuses
        # so in template we can have one line per type with all statuses in same line
        # also append a "total" count at the end of every type status list
        grouping_keys = ('kind', 'hw_manufacturer', 'hw_model', 'hw_id')
        type_grouped_counts = groupby(
            type_status_counts, lambda ts: {k: ts[k] for k in grouping_keys}
        )
        # django template engine tries to convert groupy generator to list and breaks
        # for loop in template, so we need to convert to list ouselves before
        # passing to django
        # https://stackoverflow.com/a/16171518
        # also append a "total" count at the end of every type status list
        type_status_objects = []
        for key, groups in type_grouped_counts:
            groups = list(groups)
            total = {'count': sum([g['count'] for g in groups])}
            type_status_objects.append((key, groups + [total]))

        # counts by status, ignoring different hw types
        status_counts = asset_counts_status(type_status_counts)

        return {
            'assets': assets,
            'status_counts': status_counts,
            'type_status_objects': type_status_objects,
        }


@register_model_view(models.InventoryItemGroup, 'list', path='', detail=False)
class InventoryItemGroupListView(generic.ObjectListView):
    queryset = models.InventoryItemGroup.objects.add_related_count(
        models.InventoryItemGroup.objects.all(),
        models.Asset,
        'inventoryitem_groups',
        'asset_count',
        cumulative=True,
    )
    table = tables.InventoryItemGroupTable
    filterset = filtersets.InventoryItemGroupFilterSet
    filterset_form = forms.InventoryItemGroupFilterForm


@register_model_view(models.InventoryItemGroup, 'edit')
@register_model_view(models.InventoryItemGroup, 'add', detail=False)
class InventoryItemGroupEditView(generic.ObjectEditView):
    queryset = models.InventoryItemGroup.objects.all()
    form = forms.InventoryItemGroupForm


@register_model_view(models.InventoryItemGroup, 'delete')
class InventoryItemGroupDeleteView(generic.ObjectDeleteView):
    queryset = models.InventoryItemGroup.objects.all()


@register_model_view(
    models.InventoryItemGroup, 'bulk_import', path='import', detail=False
)
class InventoryItemGroupBulkImportView(generic.BulkImportView):
    queryset = models.InventoryItemGroup.objects.all()
    model_form = forms.InventoryItemGroupImportForm


@register_model_view(models.InventoryItemGroup, 'bulk_edit', path='edit', detail=False)
class InventoryItemGroupBulkEditView(generic.BulkEditView):
    queryset = models.InventoryItemGroup.objects.all()
    filterset = filtersets.InventoryItemGroupFilterSet
    table = tables.InventoryItemGroupTable
    form = forms.InventoryItemGroupBulkEditForm


@register_model_view(
    models.InventoryItemGroup, 'bulk_delete', path='delete', detail=False
)
class InventoryItemGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = models.InventoryItemGroup.objects.all()
    filterset = filtersets.InventoryItemGroupFilterSet
    table = tables.InventoryItemGroupTable
