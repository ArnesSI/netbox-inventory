from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.db.models.signals import pre_save

from dcim.models import Device, InventoryItem, Module, Rack
from netbox.plugins import get_plugin_config

from .choices import AssetStatusChoices


def get_prechange_field(obj, field_name):
    """Get value from obj._prechange_snapshot. If field is a relation,
    return object instance.
    """
    value = getattr(obj, '_prechange_snapshot', {}).get(field_name)
    if value is None:
        return None
    field = obj._meta.get_field(field_name)
    if field.is_relation:
        rel_obj = field.related_model.objects.filter(pk=value).first()
        if rel_obj:
            return rel_obj
        else:
            return None
    return value


def get_plugin_setting(setting_name):
    return get_plugin_config('netbox_inventory', setting_name)


def get_status_for(status):
    status_name = get_plugin_setting(status + '_status_name')
    if status_name is None:
        return None
    if status_name not in dict(AssetStatusChoices):
        raise ImproperlyConfigured(
            f'netbox_inventory plugin configuration defines status {status_name}, but it is not defined in FIELD_CHOICES["netbox_inventory.Asset.status"]'
        )
    return status_name


def get_all_statuses_for(status):
    status_names = get_plugin_setting(status + '_additional_status_names')
    status_names = set(status_names)
    # add primary status
    if primary_status := get_status_for(status):
        status_names.add(primary_status)
    if len(status_names) < 1:
        return None
    if extra_statuses := status_names.difference(set(dict(AssetStatusChoices))):
        raise ImproperlyConfigured(
            f'netbox_inventory plugin configuration defines statuses {extra_statuses}, but these are not defined in FIELD_CHOICES["netbox_inventory.Asset.status"]'
        )
    return list(status_names)


def asset_clear_old_hw(old_hw):
    # need to temporarily disconnect signal receiver that prevents update of device serial if asset assigned
    from .signals import prevent_update_serial_asset_tag

    pre_save.disconnect(prevent_update_serial_asset_tag, sender=Device)
    pre_save.disconnect(prevent_update_serial_asset_tag, sender=Module)
    pre_save.disconnect(prevent_update_serial_asset_tag, sender=InventoryItem)
    pre_save.disconnect(prevent_update_serial_asset_tag, sender=Rack)
    old_hw.serial = ''
    old_hw.asset_tag = None
    old_hw.save()
    pre_save.connect(prevent_update_serial_asset_tag, sender=Device)
    pre_save.connect(prevent_update_serial_asset_tag, sender=Module)
    pre_save.connect(prevent_update_serial_asset_tag, sender=InventoryItem)
    pre_save.connect(prevent_update_serial_asset_tag, sender=Rack)


def asset_set_new_hw(asset, hw):
    """
    Asset was assigned to hardware (device/module/inventory item/rack) and we want to
    sync some field values from asset to hardware
    Validation if asset can be assigned to hw should be done before calling this function.
    """
    # device, module... needs None for blank asset_tag to enforce uniqness at DB level
    new_asset_tag = asset.asset_tag or None
    # device, module... does not allow serial to be null
    new_serial = asset.serial or ''
    hw_save = False
    if hw.serial != new_serial:
        hw.serial = new_serial
        hw_save = True
    if hw.asset_tag != new_asset_tag:
        hw.asset_tag = new_asset_tag
        hw_save = True
    # handle changing of model (<kind>_type)
    if asset.kind in ['device', 'module', 'rack']:
        asset_type = getattr(asset, asset.kind + '_type')
        hw_type = getattr(hw, asset.kind + '_type')
        if asset_type != hw_type:
            setattr(hw, asset.kind + '_type', asset_type)
            hw_save = True
    # for inventory items also set manufacturer and part_number
    if asset.inventoryitem_type:
        if hw.manufacturer != asset.inventoryitem_type.manufacturer:
            hw.manufacturer = asset.inventoryitem_type.manufacturer
            hw_save = True
        part_id = asset.inventoryitem_type.part_number
        if hw.part_id != part_id:
            hw.part_id = part_id
            hw_save = True
    if hw_save:
        hw.save()


def is_equal_none(a, b):
    """Compare a and b as string. None is considered the same as empty string."""
    if a is None or b is None:
        return a == b or a == '' or b == ''
    return a == b


def query_located(queryset, field_name, values, assets_shown='all'):
    """
    Filters queryset on located values. Can filter for installed
    location/site and/or stored location/site for assets makred as stored.
    Args:
        * queryset - queryset of Asset model
        * field_name - 'site' or 'location' or 'rack'
        * values - list of PKs of location types to filter on
        * assets_shown - 'all' or 'installed' or 'stored'
    """
    if field_name == 'rack':
        q_installed = Q(**{'rack__in': values})
    else:
        q_installed = Q(**{f'rack__{field_name}__in': values})
    q_installed = (
        q_installed
        | Q(**{f'device__{field_name}__in': values})
        | Q(**{f'module__device__{field_name}__in': values})
        | Q(**{f'inventoryitem__device__{field_name}__in': values})
    )

    # Q expressions for stored
    if field_name == 'rack':
        # storage in rack is not supported
        # generate Q() that matches none
        q_stored = Q(pk__in=[])
    elif field_name == 'location':
        q_stored = Q(**{'storage_location__in': values}) & Q(
            status__in=get_all_statuses_for('stored')
        )
    elif field_name == 'site':
        q_stored = Q(**{'storage_location__site__in': values}) & Q(
            status__in=get_all_statuses_for('stored')
        )

    if assets_shown == 'all':
        q = q_installed | q_stored
    elif assets_shown == 'installed':
        q = q_installed
    elif assets_shown == 'stored':
        q = q_stored
    else:
        raise Exception('unsupported')
    return queryset.filter(q)


def get_asset_custom_fields_search_filters():
    """Returns a list of custom field filter strings that can be used in Q() filter.

    Custom fields and filters are used is defined in the plugin configuration,
    under the key ``asset_custom_fields_search_filters``.

    Returns:
        list: list of custom field filter strings
    """
    custom_fields_filters = get_plugin_setting('asset_custom_fields_search_filters')

    fields = []
    for field_name, filters in custom_fields_filters.items():
        for filter in filters:
            fields.append(f'custom_field_data__{field_name}__{filter}')
    return fields
