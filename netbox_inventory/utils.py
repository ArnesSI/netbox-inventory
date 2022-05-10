from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .choices import InventoryStatusChoices



def get_prechange_field(obj, field_name):
    """ Get value from obj._prechange_snapshot. If field is a relation,
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
    status_name = settings.PLUGINS_CONFIG['netbox_inventory'][status+'_status_name']
    if status_name is None:
        return None
    if status_name not in dict(InventoryStatusChoices):
        raise ImproperlyConfigured(f'Configuration defines status {status_name}, but not defined in InventoryStatusChoices')
    return status_name
