from netbox.plugins import PluginConfig
from .version import __version__


class NetBoxInventoryConfig(PluginConfig):
    name = 'netbox_inventory'
    verbose_name = 'NetBox Inventory'
    version = __version__
    description = 'Inventory asset management in NetBox'
    author = 'Matej Vadnjal'
    author_email = 'matej.vadnjal@arnes.si'
    base_url = 'inventory'
    min_version = '4.1.0'
    default_settings = {
        'top_level_menu': True,
        'used_status_name': 'used',
        'stored_status_name': 'stored',
        'sync_hardware_serial_asset_tag': False,
        'asset_import_create_purchase': False,
        'asset_import_create_device_type': False,
        'asset_import_create_module_type': False,
        'asset_import_create_inventoryitem_type': False,
        'asset_import_create_tenant': False,
        'asset_disable_editing_fields_for_tags': {},
        'asset_disable_deletion_for_tags': [],
        'asset_custom_fields_search_filters': {},
        'asset_warranty_expire_warning_days': 90,
        'prefill_asset_name_create_inventoryitem': False,
        'prefill_asset_tag_create_inventoryitem': False,
    }

    def ready(self):
        super().ready()
        import netbox_inventory.signals

config = NetBoxInventoryConfig
