from dcim.models import Device, InventoryItem, Module, Rack
from netbox.views import generic

from ..forms.reassign import *

__all__ = (
    'AssetDeviceReassignView',
    'AssetModuleReassignView',
    'AssetInventoryItemReassignView',
    'AssetRackReassignView',
)


class AssetDeviceReassignView(generic.ObjectEditView):
    queryset = Device.objects.all()
    template_name = 'netbox_inventory/asset_reassign.html'
    form = AssetDeviceReassignForm


class AssetModuleReassignView(generic.ObjectEditView):
    queryset = Module.objects.all()
    template_name = 'netbox_inventory/asset_reassign.html'
    form = AssetModuleReassignForm


class AssetInventoryItemReassignView(generic.ObjectEditView):
    queryset = InventoryItem.objects.all()
    template_name = 'netbox_inventory/asset_reassign.html'
    form = AssetInventoryItemReassignForm


class AssetRackReassignView(generic.ObjectEditView):
    queryset = Rack.objects.all()
    template_name = 'netbox_inventory/asset_reassign.html'
    form = AssetRackReassignForm
