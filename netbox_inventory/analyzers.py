from copy import copy
from itertools import groupby

from django.db.models import Case, CharField, Count, F, IntegerField, Value, When
from django.db.models.functions import Concat

from dcim.models import DeviceType, ModuleType, RackType

from .choices import AssetStatusChoices
from .models import InventoryItemType


def asset_counts_type_status(assets, inventoryitem_group=None):  # noqa: C901
    """
    Return counts of assets based on combinations of hw type and status values
    for assets.
    If inventoryitem_group is given, all hw types set by group or its
    descendants are returned even there are no matching assets.
    Return value is a list of dicts, each having keys:
        - kind (one of: device, module, rack, inventoryitem)
        - hw_manufacturer (str)
        - hw_model (str)
        - hw_id (int)
        - status (str)
        - label (str, display label of status)
        - color (str, color of status)
    List is sorted by kind, manufacturer and model.
    """
    # generate counts of assets grouped by type and status
    # also annotate different type fields into one for easier processing later
    asset_counts = (
        assets.values(
            'status',
        )
        .annotate(
            count=Count('pk'),
            kind=Case(
                When(device_type__isnull=False, then=Value('device')),
                When(module_type__isnull=False, then=Value('module')),
                When(rack_type__isnull=False, then=Value('rack')),
                When(inventoryitem_type__isnull=False, then=Value('inventoryitem')),
            ),
            hw_manufacturer=Concat(
                F('device_type__manufacturer__name'),
                F('module_type__manufacturer__name'),
                F('rack_type__manufacturer__name'),
                F('inventoryitem_type__manufacturer__name'),
                output_field=CharField(),
            ),
            hw_model=Concat(
                F('device_type__model'),
                F('module_type__model'),
                F('rack_type__model'),
                F('inventoryitem_type__model'),
                output_field=CharField(),
            ),
            hw_id=Concat(
                F('device_type'),
                F('module_type'),
                F('rack_type'),
                F('inventoryitem_type'),
                output_field=IntegerField(),
            ),
        )
        .order_by(
            'kind',
            'hw_manufacturer',
            'hw_model',
            'status',
        )
    )

    def _update_status_meta(entry):
        """adds color and label keys based on status value"""
        entry['color'] = AssetStatusChoices.colors.get(entry['status'], 'gray')
        entry['label'] = dict(AssetStatusChoices).get(entry['status'], entry['status'])

    def _generate_entry(entry_from, status, count=0):
        t = copy(entry_from)
        t['status'] = status
        t['count'] = count
        _update_status_meta(t)
        return t

    # for each hw type keep track of seen statues and add any that are
    # missing with count:0
    zero_counts = []
    all_statuses = set(AssetStatusChoices.values())
    last_kind_id = None
    seen_statues = set()
    seen_kind_ids = {
        'device': set(),
        'module': set(),
        'rack': set(),
        'inventoryitem': set(),
    }
    for idx, type_status_count in enumerate(asset_counts):
        _update_status_meta(type_status_count)
        seen_kind_ids[type_status_count['kind']].add(type_status_count['hw_id'])
        if last_kind_id is None:
            last_kind_id = (type_status_count['kind'], type_status_count['hw_id'])
        if last_kind_id != (type_status_count['kind'], type_status_count['hw_id']):
            # next kind_id, add unseen statuses of previous kind_id
            for missing_status in all_statuses - seen_statues:
                zero_counts.append(
                    _generate_entry(asset_counts[idx - 1], missing_status)
                )
            # reset
            seen_statues = set()
        last_kind_id = (type_status_count['kind'], type_status_count['hw_id'])
        seen_statues.add(type_status_count['status'])
    # complete missing statues for the last inventoryitem_type in asset_counts
    if last_kind_id:
        for missing_status in all_statuses - seen_statues:
            zero_counts.append(_generate_entry(type_status_count, missing_status))

    hw_types = (
        ('device', DeviceType),
        ('module', ModuleType),
        ('rack', RackType),
        ('inventoryitem', InventoryItemType),
    )
    if inventoryitem_group:
        groups = inventoryitem_group.get_descendants(include_self=True)
        for kind, cls in hw_types:
            hw_types = (
                cls.objects.filter(inventoryitem_groups__in=groups)
                .exclude(pk__in=seen_kind_ids[kind])
                .annotate(
                    count=Value(0),
                    kind=Value(kind),
                    hw_manufacturer=F('manufacturer__name'),
                    hw_model=F('model'),
                    hw_id=F('id'),
                )
                .values(
                    'count',
                    'kind',
                    'hw_manufacturer',
                    'hw_model',
                    'hw_id',
                )
                .order_by(
                    'kind',
                    'hw_manufacturer',
                    'hw_model',
                )
            )
            for hw_type in hw_types:
                for status in all_statuses:
                    zero_counts.append(_generate_entry(hw_type, status))

    # combine non-zero and zero counts and sort
    asset_counts = sorted(
        list(asset_counts) + zero_counts,
        key=lambda k: (
            k['kind'],
            k['hw_manufacturer'],
            k['hw_model'],
            AssetStatusChoices.values().index(k['status']),
        ),
    )
    return asset_counts


def asset_counts_status(asset_counts):
    """
    Aggregates asset counts broken down by hw item type and status
    (as returned by asset_counts_type_status) to counts on just status values.
    """

    # ensures sorting by status preserves order as defined in config
    def _status_index(el):
        try:
            return AssetStatusChoices.values().index(el['status'])
        except ValueError:
            # status exists in DB but was removed from configuration
            return 9999

    status_counts = []
    status_keys = ('status', 'label', 'color')
    status_groups = groupby(
        sorted(asset_counts, key=_status_index),
        lambda ts: {k: ts[k] for k in status_keys},
    )
    for status, group in status_groups:
        status_counts.append(status | {'count': sum(t['count'] for t in group)})
    return status_counts
