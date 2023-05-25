from netbox.views import generic

from .. import filtersets, forms, models, tables
from ..choices import AssetStatusChoices
from ..analyzers import asset_counts_type_status, asset_counts_status

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
        )
        child_groups = models.InventoryItemGroup.objects.add_related_count(
            child_groups,
            models.InventoryItemType,
            'inventoryitem_group',
            'inventoryitem_type_count',
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

        # get counts for each inventoryitem type and status combination
        type_status_counts = asset_counts_type_status(instance, assets)

        # change structure of stored objects
        type_status_objects = []
        prev_type = 0
        asset_obj = {}
        total_items = len(type_status_counts)-1 # get last index
        for idx, tsc in enumerate(type_status_counts):
            if prev_type != tsc['inventoryitem_type']:
                prev_type = tsc['inventoryitem_type']
                # make sure skip first insert
                if len(asset_obj.keys()) != 0:
                    type_status_objects.append(asset_obj)
                asset_obj = {}

            # collection of statuses for same types
            status_list = { 
                'status': tsc['status'],
                'count': str(tsc['count']), # needs to be a string to render
                'color': tsc['color'],
                'label': tsc['label']
            }
            if len(asset_obj.keys()) != 0:
                asset_obj.get('status_list').append(status_list)
            else:
                # initial list of assets
                asset_obj = {
                    'inventoryitem_type__manufacturer__name': tsc['inventoryitem_type__manufacturer__name'],
                    'inventoryitem_type__model': tsc['inventoryitem_type__model'],
                    'inventoryitem_type': tsc['inventoryitem_type'],
                    'status_list': [status_list]
                }
            
            # make sure we dont forget last item
            if(total_items == idx):
                type_status_objects.append(asset_obj)
        
        # counts by status, ignoring different inventoryitem_types
        status_counts = asset_counts_status(type_status_counts)

        return {
            'child_groups_table': child_groups_table,
            'asset_table': asset_table,
            'type_status_counts': type_status_counts,
            'status_counts': status_counts,
            'type_status_objects': type_status_objects
        }


class InventoryItemGroupListView(generic.ObjectListView):
    queryset = models.InventoryItemGroup.objects.add_related_count(
        models.InventoryItemGroup.objects.all(),
        models.Asset,
        'inventoryitem_type__inventoryitem_group',
        'asset_count',
        cumulative=True
    )
    queryset = models.InventoryItemGroup.objects.add_related_count(
        queryset,
        models.InventoryItemType,
        'inventoryitem_group',
        'inventoryitem_type_count',
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
    model_form = forms.InventoryItemGroupImportForm


class InventoryItemGroupBulkEditView(generic.BulkEditView):
    queryset = models.InventoryItemGroup.objects.all()
    filterset = filtersets.InventoryItemGroupFilterSet
    table = tables.InventoryItemGroupTable
    form = forms.InventoryItemGroupBulkEditForm


class InventoryItemGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = models.InventoryItemGroup.objects.all()
    table = tables.InventoryItemGroupTable
