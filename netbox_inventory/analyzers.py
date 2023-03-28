from copy import copy
from django.db.models import Count, F

from .choices import AssetStatusChoices
from .models import Asset


def asset_counts_type_status(inventoryitem_group, assets=None):
    """
    Return counts of assets based on combinations of inventoryitem type
    and status values for assets that belong to an inventoryitem group.
    Can optionally accept pre-filtered queryset with assets.
    Return value is a list of dicts, each having keys:
        - inventoryitem_type__manufacturer__name
        - inventoryitem_type__model
        - inventoryitem_type (ID)
        - status
        - label (display label of status)
        - color (color of status)
    """
    if assets is None:
        assets = Asset.objects.all()
    assets = assets.filter(
        inventoryitem_type__inventoryitem_group__in=inventoryitem_group.get_descendants(include_self=True)
    )
    # generate counts of assets grouped by type and status
    asset_counts = assets.values(
        'inventoryitem_type__manufacturer__name',
        'inventoryitem_type__model',
        'inventoryitem_type',
        'status',
    ).annotate(
        count=Count('pk')
    ).order_by('inventoryitem_type', 'status')

    def _update_status_meta(entry):
        """ adds color and label keys based on status value """
        entry['color'] = AssetStatusChoices.colors.get(entry['status'], 'gray')
        entry['label'] = dict(AssetStatusChoices).get(entry['status'], entry['status'])

    def _generate_entry(entry_from, status, count=0):
        t = copy(entry_from)
        t['status'] = status
        t['count'] = count
        _update_status_meta(t)
        return t

    # for each inventoryitem_type keep track of seen statues and add any that are
    # missing with count:0 
    zero_counts = []
    all_statuses = set(AssetStatusChoices.values())
    last_iid_pk = None
    seen_statues = set()
    seen_iit_pks = set()
    for idx, iit_status_count in enumerate(asset_counts):
        _update_status_meta(iit_status_count)
        seen_iit_pks.add(iit_status_count['inventoryitem_type'])
        if last_iid_pk is None:
            last_iid_pk = iit_status_count['inventoryitem_type']
        if last_iid_pk != iit_status_count['inventoryitem_type']:
            # next iit_pk, add unseen statuses of previous pk
            for missing_status in all_statuses - seen_statues:
                zero_counts.append(_generate_entry(asset_counts[idx-1], missing_status))
            # reset
            seen_statues = set()
        last_iid_pk = iit_status_count['inventoryitem_type']
        seen_statues.add(iit_status_count['status'])
    # complete missing statues for the last inventoryitem_type in asset_counts
    if last_iid_pk:
        for missing_status in all_statuses - seen_statues:
            zero_counts.append(_generate_entry(iit_status_count, missing_status))

    # now add entries for inventory item types that have no assets at all
    for iit in inventoryitem_group.inventoryitem_types.exclude(pk__in=seen_iit_pks).annotate(
        inventoryitem_type__manufacturer__name=F('manufacturer__name'),
        inventoryitem_type__model=F('model'),
        inventoryitem_type=F('pk'),
    ).values(
        'inventoryitem_type__manufacturer__name',
        'inventoryitem_type__model',
        'inventoryitem_type'
    ):
        for status in all_statuses:
            zero_counts.append(_generate_entry(iit, status))

    # combine non-zero and zero counts and sort
    asset_counts = sorted(
        list(asset_counts) + zero_counts,
        key=lambda k: (k['inventoryitem_type__manufacturer__name'], k['inventoryitem_type__model'], AssetStatusChoices.values().index(k['status']))
    )
    return asset_counts


def asset_counts_status(asset_counts):
    """
    Aggregates asset counts broken down by inventory item type and status
    (as returned by asset_counts_type_status) to counts on just status valuies.
    """
    status_counts = {
        k: {
            'value': k,
            'label': l,
            'color': AssetStatusChoices.colors[k],
            'count': sum(map(
                lambda e: e['count'],
                filter(lambda e: e['status']==k, asset_counts)
            ))
        }
        for k,l in list(AssetStatusChoices)
    }
    return status_counts
