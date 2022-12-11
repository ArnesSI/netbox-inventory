import logging

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

from dcim.forms import DeviceForm, InventoryItemForm, ModuleForm
from dcim.models.device_components import ConsolePort, ConsoleServerPort, FrontPort, Interface, PowerOutlet, PowerPort, RearPort
from utilities.forms import DynamicModelChoiceField, StaticSelect

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
            self.initial['serial'] = asset.serial
            self.initial['asset_tag'] = asset.asset_tag if asset.asset_tag else None

            self.fields['manufacturer'].widget = StaticSelect(attrs={'readonly':True, 'disabled':True})
            self.fields['manufacturer'].choices = [(asset.hardware_type.manufacturer.pk, asset.hardware_type.manufacturer)]
            self.fields[kind_type].widget = StaticSelect(attrs={'readonly':True, 'disabled':True})
            self.fields[kind_type].choices = [(asset.hardware_type.pk, asset.hardware_type)]
            # disabled Select field will not be POSTed so clean() complains if field is required
            # we set value later in clean_*_type() anyway
            self.fields[kind_type].required = False

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

    consoleport = DynamicModelChoiceField(
        queryset=ConsolePort.objects.all(),
        query_params={'device_id': '$device'},
        label='Console port',
        required=False,
    )
    consoleserverport = DynamicModelChoiceField(
        queryset=ConsoleServerPort.objects.all(),
        query_params={'device_id': '$device'},
        label='Console server port',
        required=False,
    )
    frontport = DynamicModelChoiceField(
        queryset=FrontPort.objects.all(),
        query_params={'device_id': '$device'},
        label='Front port',
        required=False,
    )
    interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        query_params={'device_id': '$device'},
        label='Interface',
        required=False,
    )
    poweroutlet = DynamicModelChoiceField(
        queryset=PowerOutlet.objects.all(),
        query_params={'device_id': '$device'},
        label='Power outlet',
        required=False,
    )
    powerport = DynamicModelChoiceField(
        queryset=PowerPort.objects.all(),
        query_params={'device_id': '$device'},
        label='Power port',
        required=False,
    )
    rearport = DynamicModelChoiceField(
        queryset=RearPort.objects.all(),
        query_params={'device_id': '$device'},
        label='Rear port',
        required=False,
    )

    fieldsets = (
        InventoryItemForm.fieldsets[0],
        ('Component', ('interface', 'consoleport', 'consoleserverport', 'frontport', 'rearport', 'poweroutlet', 'powerport')),
    ) + InventoryItemForm.fieldsets[1:]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.assigned_asset:
            asset = self.instance.assigned_asset
            self.fields['serial'].disabled = True
            self.fields['asset_tag'].disabled = True
            self.fields['part_id'].disabled = True
            self.initial['serial'] = asset.serial
            self.initial['asset_tag'] = asset.asset_tag if asset.asset_tag else None
            self.initial['part_id'] = asset.inventoryitem_type.part_number

            self.fields['manufacturer'].widget = StaticSelect(attrs={'readonly':True, 'disabled':True})
            self.fields['manufacturer'].choices = [(asset.inventoryitem_type.manufacturer.pk, asset.inventoryitem_type.manufacturer)]

    def clean(self):
        cleaned_data = super().clean()
        component_set = None
        for field_name in COMPONENT_FIELDS:
            field_value = cleaned_data.get(field_name)
            if field_value and component_set:
                raise ValidationError('Only a single component can be selected')
            if field_value:
                component_set = field_name
                cleaned_data['component_type'] = ContentType.objects.get(app_label='dcim', model=field_name)
                cleaned_data['component_id'] = field_value.pk
                cleaned_data.pop(field_name)
        return cleaned_data

    def clean_manufacturer(self):
        return self.instance.assigned_asset.inventoryitem_type.manufacturer
