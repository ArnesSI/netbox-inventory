from django import forms

from dcim.models import Device, InventoryItem, Module
from netbox.forms import NetBoxModelForm
from utilities.forms import APISelect, DynamicModelChoiceField
from ..models import Asset

__all__ = (
    'AssetAssignDeviceForm',
    'AssetAssignModuleForm',
    'AssetAssignInventoryItemForm',
)


class AssetAssignDeviceForm(NetBoxModelForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        query_params={'device_type_id': '$device_type'},
        label='Device',
        required=False,
        widget=APISelect(
            api_url='/api/plugins/inventory/devices/',
            attrs={
                'data-static-params': '[{"queryParam":"has_asset_assigned","queryValue":"false"}]',
            },
        )
    )
    tags = None

    class Meta:
        model = Asset
        fields = ('device_type', 'device', 'name')
        widgets = {
            'device_type': forms.HiddenInput(),
        }

    def clean_device(self):
        device = self.cleaned_data['device']
        if device:
            if device.device_type != self.instance.device_type:
                raise forms.ValidationError('Device type of selected device does not match asset device type')

            if Asset.objects.filter(device=device).exists():
                raise forms.ValidationError(f'Device {device} already has asset assigned')

        self.instance.device = device
        return device


class AssetAssignModuleForm(NetBoxModelForm):
    module = DynamicModelChoiceField(
        queryset=Module.objects.all(),
        query_params={'module_type_id': '$module_type'},
        label='Module',
        required=False,
    )
    tags = None

    class Meta:
        model = Asset
        fields = ('module_type', 'module', 'name')
        widgets = {
            'module_type': forms.HiddenInput(),
        }

    def clean_module(self):
        module = self.cleaned_data['module']
        if module:
            if module.module_type != self.instance.module_type:
                raise forms.ValidationError('Module type of selected module does not match asset module type')

            if Asset.objects.filter(module=module).exists():
                raise forms.ValidationError(f'Module {module} already has asset assigned')

        self.instance.module = module
        return module


class AssetAssignInventoryItemForm(NetBoxModelForm):
    inventoryitem = DynamicModelChoiceField(
        queryset=InventoryItem.objects.all(),
        #query_params={'inventoryitem_type_id': '$inventoryitem_type'},
        label='Inventory item',
        required=False,
    )
    tags = None

    class Meta:
        model = Asset
        fields = ('inventoryitem_type', 'inventoryitem', 'name')
        widgets = {
            'inventoryitem_type': forms.HiddenInput(),
        }

    def clean_inventoryitem(self):
        inventoryitem = self.cleaned_data['inventoryitem']
        if inventoryitem:
            # FIXME InventoryItem does not have FK to InventoryItemType
            #if inventoryitem.inventoryitem_type != self.instance.inventoryitem_type:
            #    raise forms.ValidationError('Inventoryitem type of selected inventoryitem does not match asset inventoryitem type')

            if Asset.objects.filter(inventoryitem=inventoryitem).exists():
                raise forms.ValidationError(f'Inventoryitem {inventoryitem} already has asset assigned')

        self.instance.inventoryitem = inventoryitem
        return inventoryitem
