import logging

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

from dcim.forms import DeviceForm, InventoryItemForm, ModuleForm
from dcim.models import Device
from utilities.forms.fields import DynamicModelChoiceField
from ..utils import get_plugin_setting

__all__ = (
    'AssetDeviceCreateForm',
    'AssetModuleCreateForm',
    'AssetInventoryItemCreateForm',
)


COMPONENT_FIELDS = (
    'consoleport',
    'consoleserverport',
    'frontport',
    'interface',
    'poweroutlet',
    'powerport',
    'rearport',
)

logger = logging.getLogger('netbox.netbox_inventory.forms.create')


class AssetCreateMixin:
    def update_hardware_fields(self, kind_type):
        """
            Pre-populate and disable hardware related fields from asset data
        """
        if self.instance.assigned_asset:
            asset = self.instance.assigned_asset
            self.fields['serial'].disabled = True
            self.fields['asset_tag'].disabled = True
            self.fields[kind_type].disabled = True
            self.initial['serial'] = asset.serial
            self.initial['asset_tag'] = asset.asset_tag if asset.asset_tag else None
            self.initial[kind_type] = asset.hardware_type.id

    def save(self, *args):
        """
        After we save new hardware (Device, Module, InventortyItem), we must update
        asset.device/.module/.intentory_item to reffer to this new hardware instance
        """
        asset = self.instance.assigned_asset
        instance = super().save(*args)
        asset.snapshot()
        setattr(asset, asset.kind, instance)
        asset.full_clean()
        asset.save()
        logger.info(f'Assigned newly created hardware ({instance}) to asset {asset}')
        return instance


class AssetDeviceCreateForm(AssetCreateMixin, DeviceForm):
    """
        Populates and disables editing of asset and devcie_type fields
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_hardware_fields('device_type')

    def clean_device_type(self):
        # no mattter what was POSTed, device_type cannot be changed/missing...
        return self.instance.assigned_asset.device_type


class AssetModuleCreateForm(AssetCreateMixin, ModuleForm):
    """
        Populates and disables editing of asset and module_type fields
    """
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        selector=True,
        initial_params={
            'modulebays': '$module_bay'
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_hardware_fields('module_type')

    def clean_module_type(self):
        return self.instance.assigned_asset.module_type


class AssetInventoryItemCreateForm(AssetCreateMixin, InventoryItemForm):
    """
        Populates and disables editing of hardware related fields
        Offers selection of device components and maps selected component
        to component_type and component_id fields
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.assigned_asset:
            asset = self.instance.assigned_asset
            self.fields['serial'].disabled = True
            self.fields['asset_tag'].disabled = True
            self.fields['part_id'].disabled = True
            self.fields['manufacturer'].disabled = True
            self.initial['serial'] = asset.serial
            self.initial['asset_tag'] = asset.asset_tag if asset.asset_tag else None
            self.initial['part_id'] = asset.inventoryitem_type.part_number or asset.inventoryitem_type.model
            self.initial['manufacturer'] = asset.inventoryitem_type.manufacturer_id

            if get_plugin_setting('prefill_asset_name_create_inventoryitem'):
                self.initial['name'] = asset.name if asset.name else None
            if get_plugin_setting('prefill_asset_tag_create_inventoryitem'):
                self.initial['tags'] = asset.tags.all() if asset.tags else None

    def clean(self):
        super().clean()
        component_set = None
        for field_name in COMPONENT_FIELDS:
            field_value = self.cleaned_data.get(field_name)
            if field_value and component_set:
                raise ValidationError('Only a single component can be selected')
            if field_value:
                component_set = field_name
                self.cleaned_data['component_type'] = ContentType.objects.get(app_label='dcim', model=field_name)
                self.cleaned_data['component_id'] = field_value.pk
                self.cleaned_data.pop(field_name)

    def clean_manufacturer(self):
        return self.instance.assigned_asset.inventoryitem_type.manufacturer
