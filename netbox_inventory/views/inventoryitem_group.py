from collections import OrderedDict
from django.db.models import Count

from netbox.views import generic
from utilities.utils import count_related
from .. import filtersets, forms, models, tables
from ..choices import AssetStatusChoices

__all__ = (
    'InventoryItemGroupView',
    'InventoryItemGroupListView',
    'InventoryItemGroupEditView',
    'InventoryItemGroupDeleteView',
    'InventoryItemGroupBulkImportView',
    'InventoryItemGroupBulkEditView',
    'InventoryItemGroupBulkDeleteView',
)

class InventoryItemGroupView(generic.ObjectView):
    queryset = models.InventoryItemGroup.objects.all()

    def get_extra_context(self, request, instance):
        # build a table fo child groups with asset count
        child_groups = models.InventoryItemGroup.objects.add_related_count(
            models.InventoryItemGroup.objects.all(),
            models.Asset,
            'inventoryitem_type__inventoryitem_group',
            'asset_count',
            cumulative=True
        ).restrict(request.user, 'view').filter(
            parent__in=instance.get_descendants(include_self=True)
        )
        child_groups_table = tables.InventoryItemGroupTable(child_groups)
        child_groups_table.columns.hide('actions')
        # get all assets from this group and its descendants
        assets = models.Asset.objects.restrict(request.user, 'view').filter(
            inventoryitem_type__inventoryitem_group__in=instance.get_descendants(include_self=True)
        )
        # make table of assets
        asset_table = tables.AssetTable(assets, user=request.user)
        asset_table.columns.hide('kind')
        asset_table.configure(request)
        # generate counts of assets grouped by type and status
        asset_counts_qs = assets.values(
            "inventoryitem_type", "status",
        ).annotate(
            count=Count("status")
        ).order_by("inventoryitem_type__manufacturer__name", "inventoryitem_type__model", "status")
        # counts by status, ignoring different inventoryitem_types
        # asset_counts_qs queryset is missing combinations where count is 0
        # so we generate a list with all combinations
        status_counts = {
            k: {'value': k, 'label': l, 'color': AssetStatusChoices.colors[k], 'count': 0}
            for k,l in list(AssetStatusChoices)
        }
        items_by_status = OrderedDict()
        for ac in asset_counts_qs:
            if ac['inventoryitem_type'] not in items_by_status:
                it = models.InventoryItemType.objects.get(id=ac['inventoryitem_type'])
                items_by_status[ac['inventoryitem_type']] = dict(
                            inventoryitem_type=it,
                )
                items_by_status[ac['inventoryitem_type']]['statuses'] = {
                            k: {'value': k, 'label': l, 'color': AssetStatusChoices.colors[k], 'count': 0}
                            for k,l in list(AssetStatusChoices)
                }
            items_by_status[ac['inventoryitem_type']]['statuses'][ac['status']]['count'] = ac['count']
            status_counts[ac['status']]['count'] += ac['count']
        # flatten nested dicts into list of dicts
        asset_counts = list()
        for i in items_by_status.values():
            for status in AssetStatusChoices:
                line = dict(
                    inventoryitem_type=i['inventoryitem_type'],
                )
                line.update(i['statuses'][status[0]])
                asset_counts.append(line)

        return {
            'child_groups_table': child_groups_table,
            'asset_table': asset_table,
            'asset_counts': asset_counts,
            'status_counts': status_counts,
            'status_text': dict(AssetStatusChoices),
            'status_color': AssetStatusChoices.colors,
        }


class InventoryItemGroupListView(generic.ObjectListView):
    queryset = models.InventoryItemGroup.objects.add_related_count(
        models.InventoryItemGroup.objects.all(),
        models.Asset,
        'inventoryitem_type__inventoryitem_group',
        'asset_count',
        cumulative=True
    )
    table = tables.InventoryItemGroupTable
    filterset = filtersets.InventoryItemGroupFilterSet
    filterset_form = forms.InventoryItemGroupFilterForm


class InventoryItemGroupEditView(generic.ObjectEditView):
    queryset = models.InventoryItemGroup.objects.all()
    form = forms.InventoryItemGroupForm


class InventoryItemGroupDeleteView(generic.ObjectDeleteView):
    queryset = models.InventoryItemGroup.objects.all()


class InventoryItemGroupBulkImportView(generic.BulkImportView):
    queryset = models.InventoryItemGroup.objects.all()   
    table = tables.InventoryItemGroupTable 
    model_form = forms.InventoryItemGroupImportForm


class InventoryItemGroupBulkEditView(generic.BulkEditView):
    queryset = models.InventoryItemGroup.objects.all()
    filterset = filtersets.InventoryItemGroupFilterSet
    table = tables.InventoryItemGroupTable
    form = forms.InventoryItemGroupBulkEditForm


class InventoryItemGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = models.InventoryItemGroup.objects.all()
    table = tables.InventoryItemGroupTable
