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
    #'InventoryItemGroupBulkImportView',
    #'InventoryItemGroupBulkEditView',
    'InventoryItemGroupBulkDeleteView',
)

class InventoryItemGroupView(generic.ObjectView):
    queryset = models.InventoryItemGroup.objects.all()

    def get_extra_context(self, request, instance):
        assets = models.Asset.objects.restrict(request.user, 'view').filter(
            inventoryitem_type__inventoryitem_group=instance
        )
        asset_table = tables.AssetTable(assets, user=request.user)
        asset_table.columns.hide('kind')
        asset_table.columns.hide('inventoryitem_group')
        asset_table.configure(request)

        # generate counts of assets grouped by type and status
        asset_counts_qs = models.Asset.objects.filter(
            inventoryitem_type__inventoryitem_group=instance
        ).values(
            "inventoryitem_type", "status",
        ).annotate(
            count=Count("status")
        ).order_by("inventoryitem_type__manufacturer__name", "inventoryitem_type__model", "status")
        
        # counts by status, ignoring different inventoryitem_types
        status_counts = {
            k: {'value': k, 'label': l, 'color': AssetStatusChoices.colors[k], 'count': 0}
            for k,l in list(AssetStatusChoices)
        }

        # above queryset is missing combinations where count is 0
        # so we generate a list with all combinations
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
            'asset_table': asset_table,
            'asset_total': models.Asset.objects.filter(
                inventoryitem_type__inventoryitem_group=instance
            ).count(),
            'asset_counts': asset_counts,
            'status_counts': status_counts,
            'status_text': dict(AssetStatusChoices),
            'status_color': AssetStatusChoices.colors,
        }


class InventoryItemGroupListView(generic.ObjectListView):
    queryset = models.InventoryItemGroup.objects.annotate(
        inventoryitemtype_count=count_related(models.InventoryItemType, 'inventoryitem_group'),
        asset_count=count_related(models.Asset, 'inventoryitem_type__inventoryitem_group'),
    )
    table = tables.InventoryItemGroupTable
    filterset = filtersets.InventoryItemGroupFilterSet
    filterset_form = forms.InventoryItemGroupFilterForm


class InventoryItemGroupEditView(generic.ObjectEditView):
    queryset = models.InventoryItemGroup.objects.all()
    form = forms.InventoryItemGroupForm


class InventoryItemGroupDeleteView(generic.ObjectDeleteView):
    queryset = models.InventoryItemGroup.objects.all()


# class InventoryItemGroupBulkImportView(generic.BulkImportView):
#     queryset = models.InventoryItemGroup.objects.all()   
#     table = tables.InventoryItemGroupTable 
#     model_form = forms.InventoryItemGroupCSVForm


# class InventoryItemGroupBulkEditView(generic.BulkEditView):
#     queryset = models.InventoryItemGroup.objects.all()
#     filterset = filtersets.InventoryItemGroupFilterSet
#     table = tables.InventoryItemGroupTable
#     form = forms.InventoryItemGroupBulkEditForm


class InventoryItemGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = models.InventoryItemGroup.objects.all()
    table = tables.InventoryItemGroupTable
