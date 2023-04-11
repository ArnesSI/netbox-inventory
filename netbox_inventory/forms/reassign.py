from django import forms
from django.core.exceptions import ValidationError

from dcim.models import Device, InventoryItem, Module, Site, Location, Manufacturer
from netbox.forms import NetBoxModelForm
from utilities.forms import DynamicModelChoiceField, ChoiceField
from ..choices import AssetStatusChoices
from ..models import Asset, InventoryItemType, InventoryItemGroup
from ..utils import get_status_for


__all__ = (
    'AssetDeviceReassignForm',
    'AssetModuleReassignForm',
    'AssetInventoryItemReassignForm',
)


class AssetReassignMixin(forms.Form):
    storage_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        help_text='Limit New Asset choices only to assets stored at this site',
    )
    storage_location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={'site_id': '$storage_site',},
        help_text='Limit New Asset choices only to assets stored at this location',
    )
    asset_status = ChoiceField(
        choices=AssetStatusChoices,
        initial=get_status_for('stored'),
        label='Old Asset Status',
        help_text='Status to set to existing asset that is being unassigned',
    )
    tags = None

    class Meta:
        fields = ('storage_site', 'storage_location', 'assigned_asset', 'asset_status')

    def save(self, commit=True):
        # if existing assigned_asset, clear assignment before save
        # handle snapshot for ald and new asset
        """
        Save this form's self.instance object if commit=True. Otherwise, add
        a save_m2m() method to the form which can be called after the instance
        is saved manually at a later time. Return the model instance.
        """
        if self.errors:
            raise ValueError(
                "The %s could not be %s because the data didn't validate."
                % (
                    self.instance._meta.object_name,
                    "created" if self.instance._state.adding else "changed",
                )
            )
        if commit:
            self.instance.snapshot()
            if self.old_asset:
                self.old_asset.status = self.cleaned_data['asset_status']
                # if assigning another asset, don't clear data from device object
                # will overwrite via net_asset.save later
                # this is to avoind creating two changelog entries for device
                self.old_asset.save(clear_old_hw=not bool(self.new_asset))
            if self.new_asset:
                self.new_asset.save()
        return self.instance

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)
        if self.errors:
            return cleaned_data
        try:
            self.old_asset = self.instance.assigned_asset
        except Asset.DoesNotExist:
            # no asset currently assigned
            self.old_asset = None
        self.new_asset = self.cleaned_data['assigned_asset']
        if self.old_asset == self.new_asset:
            raise ValidationError('Cannot reasign the same asset as is already assigned')
        # set device/module for asset and clean/validate
        if self.old_asset:
            self._clean_asset(self.old_asset, None)
        if self.new_asset:
            self._clean_asset(self.new_asset, self.instance)
        return cleaned_data

    def _clean_asset(self, asset, instance):
        # store old state of asset objects for changelog
        asset.snapshot()
        try:
            # update hardware assignment and validate data
            setattr(asset, asset.kind, instance)
            asset.clean()
        except ValidationError as e:
            # ValidationError raised for device or module field
            # "remap" to error for whole form 
            raise ValidationError(e.messages)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.instance.assigned_asset
        except Asset.DoesNotExist:
            # no asset currently assigned, hide status field for old asset
            self.fields['asset_status'].widget = forms.HiddenInput()


class AssetDeviceReassignForm(AssetReassignMixin, NetBoxModelForm):
    assigned_asset = DynamicModelChoiceField(
        queryset=Asset.objects.filter(device_type__isnull=False, device__isnull=True),
        required=False,
        query_params={
            'kind': 'device',
            'is_assigned': False,
            'device_type_id': '$device_type',
            'storage_site_id': '$storage_site',
            'storage_location_id': '$storage_location',
        },
        label='New Asset',
        help_text='New asset to assign to device',
    )

    class Meta:
        model = Device
        # device_type is here only to allow setting assigned_asset query_params on device_type
        fields = AssetReassignMixin.Meta.fields + ('device_type',)
        widgets = {'device_type': forms.HiddenInput,}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # limit asset selection based on current device.device_type
        self.initial['device_type'] = self.instance.device_type_id
        assigned_asset_field = self.fields['assigned_asset']
        assigned_asset_field.queryset = Asset.objects.filter(device_type=self.instance.device_type, device__isnull=True)


class AssetModuleReassignForm(AssetReassignMixin, NetBoxModelForm):
    assigned_asset = DynamicModelChoiceField(
        queryset=Asset.objects.filter(module_type__isnull=False, module__isnull=True),
        required=False,
        query_params={
            'kind': 'module',
            'is_assigned': False,
            'module_type_id': '$module_type',
            'storage_site_id': '$storage_site',
            'storage_location_id': '$storage_location',
        },
        label='New Asset',
        help_text='New asset to assign to module',
    )

    class Meta:
        model = Module
        # module_type is here only to allow setting assigned_asset query_params on module_type
        fields = AssetReassignMixin.Meta.fields + ('module_type',)
        widgets = {'module_type': forms.HiddenInput,}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # limit asset selection based on current module.module_type
        self.initial['module_type'] = self.instance.module_type_id
        assigned_asset_field = self.fields['assigned_asset']
        assigned_asset_field.queryset = Asset.objects.filter(module_type=self.instance.module_type, module__isnull=True)


class AssetInventoryItemReassignForm(AssetReassignMixin, NetBoxModelForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        help_text='Limit New Asset choices only to assets by this manufacturer',
    )
    inventoryitem_group = DynamicModelChoiceField(
        queryset=InventoryItemGroup.objects.all(),
        required=False,
        label='Inventory Item Group',
        help_text='Limit New Asset choices only to assets belonging to this inventory item group',
    )
    inventoryitem_type = DynamicModelChoiceField(
        queryset=InventoryItemType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer',
            'inventoryitem_group_id': '$inventoryitem_group',
        },
        label='Inventory Item Type',
        help_text='Limit New Asset choices only to assets of this inventory item type',
    )
    assigned_asset = DynamicModelChoiceField(
        queryset=Asset.objects.filter(inventoryitem_type__isnull=False, inventoryitem__isnull=True),
        required=False,
        query_params={
            'kind': 'inventoryitem',
            'is_assigned': False,
            'storage_site_id': '$storage_site',
            'storage_location_id': '$storage_location',
            'manufacturer_id': '$manufacturer',
            'inventoryitem_type_id': '$inventoryitem_type',
            'inventoryitem_group_id': '$inventoryitem_group',
        },
        label='New Asset',
        help_text='New asset to assign to inventory item. Set to blank to remove assignment.',
    )

    class Meta:
        model = InventoryItem
        fields = ('manufacturer', 'inventoryitem_group', 'inventoryitem_type') + AssetReassignMixin.Meta.fields
