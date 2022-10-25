from django import forms

from dcim.models import Device, InventoryItem, Module, Site
from netbox.forms import NetBoxModelForm
from utilities.forms import APISelect, DynamicModelChoiceField
from ..models import Asset

__all__ = (
    'AssetDeviceAssignForm',
    'AssetModuleAssignForm',
    'AssetInventoryItemAssignForm',
)


class AssetAssignMixin(forms.Form):
    name = forms.CharField(
        required=False,
        label='Asset name',
        help_text=Asset._meta.get_field('name').help_text
    )
    tags = None

    def _clean_hardware_type(self, kind):
        hardware_type = self.cleaned_data[f'{kind}_type']
        if getattr(self.instance, f'{kind}_type') != hardware_type:
            raise forms.ValidationError(f'You are not allowed to change {kind}_type')
        return hardware_type

    def _clean_hardware(self, kind):
        """
        Args: 
            kind (str): one of device, module or inventoryitem
        """
        hardware = self.cleaned_data[kind]
        if hardware:
            instance_hardware = getattr(self.instance, kind)
            if instance_hardware == hardware:
                # field was not changed
                return hardware

            if getattr(hardware, f'{kind}_type') != getattr(self.instance, f'{kind}_type'):
                raise forms.ValidationError(f'{kind} type of selected {kind} does not match asset\'s {kind} type')

            if Asset.objects.filter(**{kind: hardware}).exists():
                raise forms.ValidationError(f'{kind} {hardware} already has asset assigned')

        setattr(self.instance, kind, hardware)
        return hardware


class AssetDeviceAssignForm(AssetAssignMixin, NetBoxModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        initial_params={'devices': '$device'},
    )
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        query_params={'device_type_id': '$device_type', 'site_id': '$site'},
        label='Device',
        required=False,
        help_text='Set to empty to unassign asset from device',
        widget=APISelect(
            api_url='/api/plugins/inventory/dcim/devices/',
            attrs={
                'data-static-params': '[{"queryParam":"has_asset_assigned","queryValue":"false"}]',
            },
        )
    )

    fieldsets = (
        ('Asset', ('device_type', 'name')),
        ('Device', ('site', 'device')),
        ('Tenancy', ('tenant', 'contact')),
    )

    class Meta:
        model = Asset
        fields = ('device_type', 'name', 'site', 'device', 'tenant', 'contact')
        widgets = {'device_type': forms.HiddenInput()}

    def clean_device_type(self):
        return self._clean_hardware_type('device')

    def clean_device(self):
        return self._clean_hardware('device')


class AssetModuleAssignForm(AssetAssignMixin, NetBoxModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        initial_params={'devices': '$device'},
    )
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        query_params={'site_id': '$site'},
        label='Device',
        required=False,
    )
    module = DynamicModelChoiceField(
        queryset=Module.objects.all(),
        query_params={'module_type_id': '$module_type', 'device_id': '$device'},
        label='Module',
        required=False,
        help_text='Set to empty to unassign asset from module',
        widget=APISelect(
            api_url='/api/plugins/inventory/dcim/modules/',
            attrs={
                'data-static-params': '[{"queryParam":"has_asset_assigned","queryValue":"false"}]',
            },
        )
    )

    fieldsets = (
        ('Asset', ('module_type', 'name')),
        ('Module', ('site', 'device', 'module')),
        ('Tenancy', ('tenant', 'contact')),
    )

    class Meta:
        model = Asset
        fields = ('module_type', 'name', 'site', 'device', 'module', 'tenant', 'contact')
        widgets = {'module_type': forms.HiddenInput()}

    def clean_device(self):
        # prevents trying to set asset.device
        return None

    def clean_module_type(self):
        return self._clean_hardware_type('module')

    def clean_module(self):
        return self._clean_hardware('module')


class AssetInventoryItemAssignForm(AssetAssignMixin, NetBoxModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        initial_params={'devices': '$device'},
    )
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        query_params={'site_id': '$site'},
        label='Device',
        required=False,
    )
    inventoryitem = DynamicModelChoiceField(
        queryset=InventoryItem.objects.all(),
        # we can't filter on inventoryitem_type because inventoryitem doesn't
        # have relation to inventoryitem_type
        query_params={'device_id': '$device'},
        label='Inventory item',
        required=False,
        help_text='Set to empty to unassign asset from inventory item',
        widget=APISelect(
            api_url='/api/plugins/inventory/dcim/inventory-items/',
            attrs={
                'data-static-params': '[{"queryParam":"has_asset_assigned","queryValue":"false"}]',
            },
        )
    )

    fieldsets = (
        ('Asset', ('inventoryitem_type', 'name')),
        ('Inventory Item', ('site', 'device', 'inventoryitem')),
        ('Tenancy', ('tenant', 'contact')),
    )

    class Meta:
        model = Asset
        fields = ('inventoryitem_type', 'name', 'site', 'device', 'inventoryitem', 'tenant', 'contact')
        widgets = {'inventoryitem_type': forms.HiddenInput()}

    def clean_device(self):
        # prevents trying to set asset.device
        return None

    def clean_inventoryitem_type(self):
        return self._clean_hardware_type('inventoryitem')

    def clean_inventoryitem(self):
        inventoryitem = self.cleaned_data['inventoryitem']
        if inventoryitem:
            if self.instance.inventoryitem == inventoryitem:
                # field was not changed
                return inventoryitem
            
            if Asset.objects.filter(inventoryitem=inventoryitem).exists():
                raise forms.ValidationError(f'Inventory item {inventoryitem} already has asset assigned')

        self.instance.inventoryitem = inventoryitem
        return inventoryitem
