from extras.plugins import PluginTemplateExtension
from .models import Asset

class DeviceAssetInfo(PluginTemplateExtension):
    model = 'dcim.device'

    def left_page(self):
        device = self.context.get('object')
        asset = Asset.objects.filter(device=device).first()
        return self.render('netbox_inventory/inc/asset_info.html', extra_context={
            'asset': asset,
        })

template_extensions = [DeviceAssetInfo]
