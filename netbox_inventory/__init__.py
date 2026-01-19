from django.apps import apps

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
    min_version = '4.5.0'
    default_settings = {
        'top_level_menu': True,
        'used_status_name': 'used',
        'used_additional_status_names': [],
        'stored_status_name': 'stored',
        'stored_additional_status_names': [
            'retired',
        ],
        'sync_hardware_serial_asset_tag': False,
        'asset_import_create_purchase': False,
        'asset_import_create_device_type': False,
        'asset_import_create_module_type': False,
        'asset_import_create_inventoryitem_type': False,
        'asset_import_create_rack_type': False,
        'asset_import_create_tenant': False,
        'asset_custom_fields_search_filters': {},
        'asset_warranty_expire_warning_days': 90,
        'prefill_asset_name_create_inventoryitem': False,
        'prefill_asset_tag_create_inventoryitem': False,
        'audit_window': 4 * 60,  # 4 hours
    }

    def register_feature_views(self) -> None:
        """
        Register feature views for all available models.
        """
        from utilities.views import register_model_view

        for model in apps.get_models():
            register_model_view(model, 'audit-trails', kwargs={'model': model})(
                'netbox_inventory.views.ObjectAuditTrailView',
            )

    def ready(self):
        super().ready()
        from . import signals  # noqa: F401

        self.register_feature_views()


config = NetBoxInventoryConfig
