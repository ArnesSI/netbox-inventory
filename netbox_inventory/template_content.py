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


class DeviceAssetInfo(AssetInfoExtension):
    model = 'dcim.device'
    kind = 'device'


class ModuleAssetInfo(AssetInfoExtension):
    model = 'dcim.module'
    kind = 'module'


class InventoryItemAssetInfo(AssetInfoExtension):
    model = 'dcim.inventoryitem'
    kind = 'inventoryitem'


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


template_extensions = (
    DeviceAssetInfo,
    ModuleAssetInfo,
    InventoryItemAssetInfo,
    TenantAssetInfo,
)
