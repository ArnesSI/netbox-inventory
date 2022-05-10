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
    min_version = '3.2.0'
    default_settings = {
        'used_status_name': 'used',
        'stored_status_name': 'stored',
        'sync_hardware_serial_asset_tag': False,
        'asset_import_create_supplier': False,
        'asset_import_create_device_type': False,
        'asset_import_create_module_type': False,
        'asset_import_create_inventoryitem_type': False,
    }

config = NetBoxInventoryConfig
