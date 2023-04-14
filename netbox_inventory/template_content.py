from extras.plugins import PluginTemplateExtension

from .models import Asset
from .utils import get_asset_warranty_context


class AssetInfoExtension(PluginTemplateExtension):
    def left_page(self):
        object = self.context.get('object')
        asset = Asset.objects.filter(**{self.kind:object}).first()
        context = {'asset': asset}
        if asset:
            context.update(get_asset_warranty_context(asset))
        return self.render('netbox_inventory/inc/asset_info.html', extra_context=context)


class AssetTypeStats(PluginTemplateExtension):
    def right_page(self):
        object = self.context.get('object')
        user = self.context['request'].user
        context = {
            'asset_stats': [
                {
                    'label': 'Total',
                    'filter_field': f'{self.kind}_id',
                    'count': Asset.objects.restrict(user, 'view').filter(**{self.kind:object}).count(),
                },
            ],
        }
        return self.render('netbox_inventory/inc/asset_stats_counts.html', extra_context=context)


class DeviceAssetInfo(AssetInfoExtension):
    model = 'dcim.device'
    kind = 'device'


class ModuleAssetInfo(AssetInfoExtension):
    model = 'dcim.module'
    kind = 'module'


class InventoryItemAssetInfo(AssetInfoExtension):
    model = 'dcim.inventoryitem'
    kind = 'inventoryitem'


class DeviceTypeAssetInfo(AssetTypeStats):
    model = 'dcim.devicetype'
    kind = 'device_type'


class ModuleTypeAssetInfo(AssetTypeStats):
    model = 'dcim.moduletype'
    kind = 'module_type'


class ManufacturerAssetInfo(PluginTemplateExtension):
    model = 'dcim.manufacturer'
    def right_page(self):
        object = self.context.get('object')
        user = self.context['request'].user
        count_device = Asset.objects.restrict(user, 'view').filter(device_type__manufacturer=object).count()
        count_module = Asset.objects.restrict(user, 'view').filter(module_type__manufacturer=object).count()
        count_inventoryitem = Asset.objects.restrict(user, 'view').filter(inventoryitem_type__manufacturer=object).count()
        context = {
            'asset_stats': [
                {
                    'label': 'Device',
                    'filter_field': 'manufacturer_id',
                    'extra_filter': '&kind=device',
                    'count': count_device,
                },
                {
                    'label': 'Module',
                    'filter_field': 'manufacturer_id',
                    'extra_filter': '&kind= module',
                    'count': count_module,
                },
                {
                    'label': 'Inventory Item',
                    'filter_field': 'manufacturer_id',
                    'extra_filter': '&kind=inventoryitem',
                    'count': count_inventoryitem,
                },
                {
                    'label': 'Total',
                    'filter_field': 'manufacturer_id',
                    'count': count_device + count_module + count_inventoryitem,
                },
            ],
        }
        return self.render('netbox_inventory/inc/asset_stats_counts.html', extra_context=context)


class TenantAssetInfo(PluginTemplateExtension):
    model = 'tenancy.tenant'
    def right_page(self):
        object = self.context.get('object')
        user = self.context['request'].user
        context = {
            'asset_assigned_count': Asset.objects.restrict(user, 'view').filter(tenant=object).count(),
            'asset_owned_count': Asset.objects.restrict(user, 'view').filter(owner=object).count(),
        }
        return self.render('netbox_inventory/inc/asset_tenant.html', extra_context=context)


class ContactAssetInfo(PluginTemplateExtension):
    model = 'tenancy.contact'
    def right_page(self):
        object = self.context.get('object')
        user = self.context['request'].user
        context = {
            'asset_stats': [
                {
                    'label': 'Assigned',
                    'filter_field': 'contact_id',
                    'count': Asset.objects.restrict(user, 'view').filter(contact=object).count(),
                },
            ],
        }
        return self.render('netbox_inventory/inc/asset_stats_counts.html', extra_context=context)


template_extensions = (
    DeviceAssetInfo,
    ModuleAssetInfo,
    InventoryItemAssetInfo,
    DeviceTypeAssetInfo,
    ModuleTypeAssetInfo,
    ManufacturerAssetInfo,
    TenantAssetInfo,
    ContactAssetInfo,
)
