from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import pre_save

from dcim.models import Device, Module, InventoryItem
from .choices import AssetStatusChoices


def get_asset_warranty_context(asset):
    warranty_progress = None
    bar_class = 'bg-success'
    if asset.warranty_elapsed and asset.warranty_elapsed.total_seconds() > 0 and asset.warranty_total:
        warranty_progress = asset.warranty_elapsed / asset.warranty_total
    if warranty_progress is not None:
        warranty_progress = warranty_progress * 100
        if asset.warranty_remaining.days < 7:
            bar_class = 'bg-danger'
        elif asset.warranty_remaining.days < 30:
            bar_class = 'bg-warning'
    return dict(
        warranty_progress=warranty_progress,
        bar_class=bar_class
    )


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
    plugin_settings = settings.PLUGINS_CONFIG['netbox_inventory']
    assert setting_name in plugin_settings, f'Setting {setting_name} not supported'
    return plugin_settings[setting_name]


def get_status_for(status):
    status_name = get_plugin_setting(status + '_status_name')
    if status_name is None:
        return None
    if status_name not in dict(AssetStatusChoices):
        raise ImproperlyConfigured(
            f'Configuration defines status {status_name}, but not defined in AssetStatusChoices'
        )
    return status_name


def get_tags_that_protect_asset_from_deletion():
    """Return a list of tags that prevent an asset from being deleted.

    Which tags prevent deletion is defined in the plugin configuration,
    under the key ``asset_disable_deletion_for_tags``.

    Returns:
        list: list of tag slug strings
    """
    return get_plugin_setting('asset_disable_deletion_for_tags')


def get_tags_and_edit_protected_asset_fields():
    """Return a dict of tags and fields that prevent editing specified fields.

    Which tags prevent editing is defined in the plugin configuration,
    under the key ``asset_disable_editing_fields_for_tags``.

    Structure of the dict is::

        {
            'tag_slug': ['field1', 'field2'],
            'tag_slug2': ['field1', 'field4'],
        }

    Returns:
        dict: dict of tag slug strings and list of field names
    """
    return get_plugin_setting('asset_disable_editing_fields_for_tags')


def asset_clear_old_hw(old_hw):
    # need to temporarily disconnect signal receiver that prevents update of device serial if asset assigned
    from .signals import prevent_update_serial_asset_tag
    pre_save.disconnect(prevent_update_serial_asset_tag, sender=Device)
    pre_save.disconnect(prevent_update_serial_asset_tag, sender=Module)
    pre_save.disconnect(prevent_update_serial_asset_tag, sender=InventoryItem)
    old_hw.serial = ''
    old_hw.asset_tag = None
    old_hw.save()
    pre_save.connect(prevent_update_serial_asset_tag, sender=Device)
    pre_save.connect(prevent_update_serial_asset_tag, sender=Module)
    pre_save.connect(prevent_update_serial_asset_tag, sender=InventoryItem)


def query_located(queryset, field_name, values, assets_shown='all'):
    """
    Filters queryset on located values. Can filter for installed
    location/site and/or stored location/site for assets makred as stored.
    Args:
        * queryset - queryset of Asset model
        * field_name - 'site' or 'location' or 'rack'
        * values - list of PKs of location types to filter on
        * assets_shown - 'all' or 'installd' or 'stored'
    """
    q_installed = (
        Q(**{f'device__{field_name}__in':values})|
        Q(**{f'module__device__{field_name}__in':values})|
        Q(**{f'inventoryitem__device__{field_name}__in':values})
    )
    if field_name == 'rack':
        # storage in rack is not supported
        # generate Q() that matches none
        q_stored = Q(pk__in=[])
    elif field_name == 'location':
        q_stored = (
            Q(**{f'storage_location__in':values})&
            Q(status=get_status_for('stored'))
        )
    else:
        q_stored = (
            Q(**{f'storage_location__{field_name}__in':values})&
            Q(status=get_status_for('stored'))
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
