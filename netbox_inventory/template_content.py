from django.db.models import Model
from django.http import HttpRequest
from django.template import Template

from core.models import ObjectType
from netbox.plugins import PluginTemplateExtension

from .models import Asset, AuditFlow
from .utils import query_located

#
# Assets
#

WARRANTY_PROGRESSBAR = """
{% with record.warranty_progress as wp %}
{% with record.warranty_remaining as wr %}
{% with settings.PLUGINS_CONFIG.netbox_inventory.asset_warranty_expire_warning_days as wthresh %}

{% if wp is None and wr.days <= 0 %}
  <div class="progress" role="progressbar">
    <div class="progress-bar progress-bar-striped text-bg-danger" style="width:100%;">
      Expired {{ record.warranty_end|timesince|split:','|first }} ago
    </div>
  </div>
{% elif wp is None and wr.days > 0 %}
  <div class="progress" role="progressbar">
    <div class="progress-bar progress-bar-striped text-bg-{% if wthresh and wr.days < wthresh %}warning{% else %}success{% endif %}" style="width:100%;">
      {{ record.warranty_end|timeuntil|split:','|first }}
    </div>
  </div>
{% elif wp is None %}
    {{ ""|placeholder }}
{% else %}

<div
  class="progress"
  role="progressbar"
  aria-valuemin="0"
  aria-valuemax="100"
  aria-valuenow="{% if wp < 0 %}0{% else %}{{ wp }}{% endif %}"
>
  <div
    class="progress-bar text-bg-{% if wp >= 100 %}danger{% elif wthresh and wr.days < wthresh %}warning{% else %}success{% endif %}"
    style="width: {% if wp < 0 %}0%{% else %}{{ wp }}%{% endif %};"
  ></div>
  {% if record.warranty_progress >= 100 %}
    <span class="justify-content-center d-flex align-items-center position-absolute text-light w-100 h-100">Expired {{ record.warranty_end|timesince|split:','|first }} ago</span>
  {% elif record.warranty_progress >= 35 %}
    <span class="justify-content-center d-flex align-items-center position-absolute text-body-emphasis w-100 h-100">{{ record.warranty_end|timeuntil|split:','|first }}</span>
  {% elif record.warranty_progress >= 0 %}
    <span class="justify-content-center d-flex align-items-center position-absolute text-body-emphasis w-100 h-100">{{ record.warranty_end|timeuntil|split:','|first }}</span>
  {% else %}
    <span class="justify-content-center d-flex align-items-center position-absolute text-body-emphasis w-100 h-100">Starts in {{ record.warranty_start|timeuntil|split:','|first }}</span>
  {% endif %}
</div>

{% endif %}
{% endwith wthresh %}
{% endwith wr %}
{% endwith wp %}
"""


class AssetInfoExtension(PluginTemplateExtension):
    def left_page(self):
        object = self.context.get('object')
        asset = Asset.objects.filter(**{self.kind: object}).first()
        context = {'asset': asset}
        context['warranty_progressbar'] = Template(WARRANTY_PROGRESSBAR)
        return self.render(
            'netbox_inventory/inc/asset_info.html', extra_context=context
        )


class AssetLocationCounts(PluginTemplateExtension):
    def right_page(self):
        object = self.context.get('object')
        user = self.context['request'].user
        assets_qs = Asset.objects.restrict(user, 'view')
        count_installed = query_located(
            assets_qs, self.location_type, [object.pk], assets_shown='installed'
        ).count()
        count_stored = query_located(
            assets_qs, self.location_type, [object.pk], assets_shown='stored'
        ).count()
        context = {
            'asset_stats': [
                {
                    'label': 'Installed',
                    'filter_field': f'installed_{self.location_type}_id',
                    'count': count_installed,
                },
                {
                    'label': 'Stored',
                    'filter_field': f'storage_{self.location_type}_id',
                    'count': count_stored,
                },
                {
                    'label': 'Total',
                    'filter_field': f'located_{self.location_type}_id',
                    'count': count_installed + count_stored,
                },
            ],
        }
        return self.render(
            'netbox_inventory/inc/asset_stats_counts.html', extra_context=context
        )


class DeviceAssetInfo(AssetInfoExtension):
    models = ['dcim.device']
    kind = 'device'


class ModuleAssetInfo(AssetInfoExtension):
    models = ['dcim.module']
    kind = 'module'


class InventoryItemAssetInfo(AssetInfoExtension):
    models = ['dcim.inventoryitem']
    kind = 'inventoryitem'


class RackAssetInfo(AssetInfoExtension):
    models = ['dcim.rack']
    kind = 'rack'


class ManufacturerAssetCounts(PluginTemplateExtension):
    models = ['dcim.manufacturer']

    def right_page(self):
        object = self.context.get('object')
        user = self.context['request'].user
        count_device = (
            Asset.objects.restrict(user, 'view')
            .filter(device_type__manufacturer=object)
            .count()
        )
        count_module = (
            Asset.objects.restrict(user, 'view')
            .filter(module_type__manufacturer=object)
            .count()
        )
        count_inventoryitem = (
            Asset.objects.restrict(user, 'view')
            .filter(inventoryitem_type__manufacturer=object)
            .count()
        )
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
                    'extra_filter': '&kind=module',
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
        return self.render(
            'netbox_inventory/inc/asset_stats_counts.html', extra_context=context
        )


class SiteAssetCounts(AssetLocationCounts):
    models = ['dcim.site']
    location_type = 'site'


class LocationAssetCounts(AssetLocationCounts):
    models = ['dcim.location']
    location_type = 'location'


class RackAssetCounts(PluginTemplateExtension):
    # rack cannot have stored assets so we can't use AssetLocationStats
    models = ['dcim.rack']

    def right_page(self):
        object = self.context.get('object')
        user = self.context['request'].user
        assets_qs = Asset.objects.restrict(user, 'view')
        assets_qs = query_located(assets_qs, 'rack', [object.pk])
        context = {
            'asset_stats': [
                {
                    'label': 'Installed',
                    'filter_field': 'installed_rack_id',
                    'count': assets_qs.count(),
                },
            ],
        }
        return self.render(
            'netbox_inventory/inc/asset_stats_counts.html', extra_context=context
        )


class TenantAssetCounts(PluginTemplateExtension):
    models = ['tenancy.tenant']

    def right_page(self):
        object = self.context.get('object')
        user = self.context['request'].user
        context = {
            'asset_stats': [
                {
                    'label': 'Assigned',
                    'filter_field': 'tenant_id',
                    'count': Asset.objects.restrict(user, 'view')
                    .filter(tenant=object)
                    .count(),
                },
                {
                    'label': 'Owned',
                    'filter_field': 'owning_tenant_id',
                    'count': Asset.objects.restrict(user, 'view')
                    .filter(owning_tenant=object)
                    .count(),
                },
            ],
        }
        return self.render(
            'netbox_inventory/inc/asset_stats_counts.html', extra_context=context
        )


class ContactAssetCounts(PluginTemplateExtension):
    models = ['tenancy.contact']

    def right_page(self):
        object = self.context.get('object')
        user = self.context['request'].user
        context = {
            'asset_stats': [
                {
                    'label': 'Assigned',
                    'filter_field': 'contact_id',
                    'count': Asset.objects.restrict(user, 'view')
                    .filter(contact=object)
                    .count(),
                },
            ],
        }
        return self.render(
            'netbox_inventory/inc/asset_stats_counts.html', extra_context=context
        )


#
# Audit
#


class AuditFlowRunButton(PluginTemplateExtension):
    """
    Add a button to start an audit flow on the detail pages of applicable objects.
    """

    models = [
        'dcim.site',
        'dcim.location',
        'dcim.rack',
    ]

    def get_object(self) -> Model:
        return self.context['object']

    def get_request(self) -> HttpRequest:
        return self.context['request']

    def get_flows(self) -> list[AuditFlow]:
        """
        Return a list of working audit flows (enabled and with pages) that apply to the
        current context object.
        """
        obj = self.get_object()
        request = self.get_request()

        object_type = ObjectType.objects.get_for_model(obj)
        flows = (
            AuditFlow.objects.filter(
                object_type=object_type,
                enabled=True,
                pages__isnull=False,  # Filter flows with no pages assigned
            )
            .restrict(request.user, 'run')
            .distinct()
        )

        return [flow for flow in flows if flow.get_objects().filter(pk=obj.pk).exists()]

    def buttons(self):
        flows = self.get_flows()
        if not flows:
            return ''

        return self.render(
            'netbox_inventory/inc/buttons/auditflow_run.html',
            extra_context={
                'flows': flows,
            },
        )


template_extensions = (
    # Assets
    DeviceAssetInfo,
    ModuleAssetInfo,
    InventoryItemAssetInfo,
    RackAssetInfo,
    ManufacturerAssetCounts,
    SiteAssetCounts,
    LocationAssetCounts,
    RackAssetCounts,
    TenantAssetCounts,
    ContactAssetCounts,
    # Audit
    AuditFlowRunButton,
)
