from dcim.models import Device, InventoryItem, Module
from netbox.views import generic
from ..forms.create import *
from ..models import Asset

__all__ = (
    'AssetDeviceCreateView',
    'AssetModuleCreateView',
    'AssetInventoryItemCreateView',
)


class AssetCreateView(generic.ObjectEditView):
    template_name = 'netbox_inventory/asset_create.html'
    asset = None

    def _load_asset(self, request):
        asset_id = request.GET.get('asset_id')
        if asset_id:
            self.asset = Asset.objects.get(pk=asset_id)

    def dispatch(self, request, *args, **kwargs):
        self._load_asset(request)
        return super().dispatch(request, *args, **kwargs)

    def alter_object(self, obj, request, url_args, url_kwargs):
        obj.assigned_asset = self.asset
        return super().alter_object(obj, request, url_args, url_kwargs)

    def get_extra_context(self, request, instance):
        context = super().get_extra_context(request, instance)
        context['asset'] = self.asset
        return context


class AssetDeviceCreateView(AssetCreateView):
    queryset = Device.objects.all()
    form = AssetDeviceCreateForm

    def get_object(self, **kwargs):
        return Device(assigned_asset=self.asset)

    def get_extra_context(self, request, instance):
        context = super().get_extra_context(request, instance)
        context['template_extends'] = 'dcim/device_edit.html'
        return context


class AssetModuleCreateView(AssetCreateView):
    queryset = Module.objects.all()
    form = AssetModuleCreateForm

    def get_object(self, **kwargs):
        return Module(assigned_asset=self.asset)


class AssetInventoryItemCreateView(AssetCreateView):
    queryset = InventoryItem.objects.all()
    form = AssetInventoryItemCreateForm

    def get_object(self, **kwargs):
        return InventoryItem(assigned_asset=self.asset)
