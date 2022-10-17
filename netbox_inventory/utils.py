from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .choices import InventoryStatusChoices


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


def get_status_for(status):
    status_name = settings.PLUGINS_CONFIG['netbox_inventory'][status + '_status_name']
    if status_name is None:
        return None
    if status_name not in dict(InventoryStatusChoices):
        raise ImproperlyConfigured(
            f'Configuration defines status {status_name}, but not defined in InventoryStatusChoices'
        )
    return status_name


def get_tags_that_protect_asset_from_deletion():
    """Return a list of tags that prevent an asset from being deleted.

    Which tags prevent deletion is defined in the plugin configuration,
    under the key ``asset_disable_deletion_for_tags``.

    Returns:
        list: list of tag slug strings
    """
    return settings.PLUGINS_CONFIG['netbox_inventory'][
        'asset_disable_deletion_for_tags'
    ]


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
    return settings.PLUGINS_CONFIG['netbox_inventory'][
        'asset_disable_editing_fields_for_tags'
    ]


