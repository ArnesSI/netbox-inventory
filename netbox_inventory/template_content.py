from extras.plugins import PluginTemplateExtension
from .models import Asset

class AssetInfoExtension(PluginTemplateExtension):
    def left_page(self):
        object = self.context.get('object')
        asset = Asset.objects.filter(**{self.kind:object}).first()
        return self.render('netbox_inventory/inc/asset_info.html', extra_context={
            'asset': asset,
        })


class DeviceAssetInfo(AssetInfoExtension):
    model = 'dcim.device'
    kind = 'device'


class ModuleAssetInfo(AssetInfoExtension):
    model = 'dcim.module'
    kind = 'module'


class InventoryItemAssetInfo(AssetInfoExtension):
    model = 'dcim.inventoryitem'
    kind = 'inventoryitem'


template_extensions = (
    DeviceAssetInfo,
    ModuleAssetInfo,
    InventoryItemAssetInfo,
)
