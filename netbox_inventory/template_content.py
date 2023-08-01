from django.template import Template
from extras.plugins import PluginTemplateExtension

from .models import Asset


WARRANTY_PROGRESSBAR = '''
{% with record.warranty_progress as wp %}
{% with record.warranty_remaining as wr %}
{% with settings.PLUGINS_CONFIG.netbox_inventory.asset_warranty_expire_warning_days as wthresh %}

{% if wp is None and wr.days <= 0 %}
    <div class="progress"><div role="progressbar" class="progress-bar progress-bar-striped bg-danger" style="width:100%;">Expired {{ record.warranty_end|timesince|split:','|first }} ago</div></div>
{% elif wp is None and wr.days > 0 %}
    <div class="progress"><div role="progressbar" class="progress-bar progress-bar-striped {% if wthresh and wr.days < wthresh %}bg-warning{% else %}bg-success{% endif %}" style="width:100%;">{{ record.warranty_end|timeuntil|split:','|first }}</div></div>
{% elif wp is None %}
    <span class="text-muted">No data</span>
{% else %}

<div class="progress">
  <div
    role="progressbar"
    aria-valuemin="0"
    aria-valuemax="100"
    aria-valuenow="{% if wp < 0 %}0{% else %}{{ wp }}{% endif %}"
    class="progress-bar {% if wp >= 100 %}bg-danger{% elif wthresh and wr.days < wthresh %}bg-warning{% else %}bg-success{% endif %}"
    style="width: {% if wp < 0 %}0%{% else %}{{ wp }}%{% endif %};"
  >
  {% if record.warranty_progress >= 100 %}
    Expired {{ record.warranty_end|timesince|split:','|first }} ago
  </div>
  {% elif record.warranty_progress >= 35 %}
    {{ record.warranty_end|timeuntil|split:','|first }}
  </div>
  {% elif record.warranty_progress >= 0 %}
  </div>
    <span class="ps-1">{{ record.warranty_end|timeuntil|split:','|first }}</span>
  {% else %}
  </div>
    <span class="text-center" style="width: 100%">Starts in {{ record.warranty_start|timeuntil|split:','|first }}</span>
  {% endif %}
</div>

{% endif %}
{% endwith wthresh %}
{% endwith wr %}
{% endwith wp %}
'''

class AssetInfoExtension(PluginTemplateExtension):
    def left_page(self):
        object = self.context.get('object')
        asset = Asset.objects.filter(**{self.kind:object}).first()
        context = {'asset': asset}
        context['warranty_progressbar'] = Template(WARRANTY_PROGRESSBAR)
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
            'asset_stats': [
                {
                    'label': 'Assigned',
                    'filter_field': 'tenant_id',
                    'count': Asset.objects.restrict(user, 'view').filter(tenant=object).count(),
                },
                {
                    'label': 'Owned',
                    'filter_field': 'owner_id',
                    'count': Asset.objects.restrict(user, 'view').filter(owner=object).count(),
                },
            ],
        }
        return self.render('netbox_inventory/inc/asset_stats_counts.html', extra_context=context)


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
