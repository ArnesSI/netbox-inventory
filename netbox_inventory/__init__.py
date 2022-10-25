from extras.plugins import PluginConfig
from .version import __version__


class NetBoxInventoryConfig(PluginConfig):
    name = 'netbox_inventory'
    verbose_name = 'NetBox Inventory'
    version = __version__
    description = 'Inventory asset management in NetBox'
    author = 'Matej Vadnjal'
    author_email = 'matej.vadnjal@arnes.si'
    base_url = 'inventory'
    min_version = '3.3.0'
    default_settings = {
        'used_status_name': 'used',
        'stored_status_name': 'stored',
        'sync_hardware_serial_asset_tag': False,
        'asset_import_create_purchase': False,
        'asset_import_create_device_type': False,
        'asset_import_create_module_type': False,
        'asset_import_create_inventoryitem_type': False,
        'asset_disable_editing_fields_for_tags': {},
        'asset_disable_deletion_for_tags': [],
    }

    def ready(self):
        super().ready()
        import netbox_inventory.signals

config = NetBoxInventoryConfig
