from dcim.forms import DeviceForm, InventoryItemForm, ModuleForm
from utilities.forms import StaticSelect

__all__ = (
    'AssetCreateDeviceForm',
    'AssetCreateModuleForm',
    'AssetCreateInventoryItemForm',
)


class AssetCreateDeviceForm(DeviceForm):
    """
        Populates and disables editing of asset and devcie_type fields
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.assigned_asset:
            asset = self.instance.assigned_asset
            self.fields['serial'].disabled = True
            self.fields['asset_tag'].disabled = True
            self.initial['serial'] = asset.serial
            self.initial['asset_tag'] = asset.asset_tag if asset.asset_tag else None

            self.fields['manufacturer'].widget = StaticSelect(attrs={'readonly':True, 'disabled':True})
            self.fields['manufacturer'].choices = [(asset.device_type.manufacturer.pk, asset.device_type.manufacturer)]
            self.fields['device_type'].widget = StaticSelect(attrs={'readonly':True, 'disabled':True})
            self.fields['device_type'].choices = [(asset.device_type.pk, asset.device_type)]
            # disabled Select field will not be POSTed so clean() complains if field is required
            # we set value later in clean_device_type() anyway
            self.fields['device_type'].required = False

    def clean_device_type(self):
        # no mattter what was POSTed, device_type cannot be changed/missing...
        return self.instance.assigned_asset.device_type


class AssetCreateModuleForm(ModuleForm):
    """
        Populates and disables editing of asset and module_type fields
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.assigned_asset:
            asset = self.instance.assigned_asset
            self.fields['serial'].disabled = True
            self.fields['asset_tag'].disabled = True
            self.initial['serial'] = asset.serial
            self.initial['asset_tag'] = asset.asset_tag if asset.asset_tag else None

            self.fields['manufacturer'].widget = StaticSelect(attrs={'readonly':True, 'disabled':True})
            self.fields['manufacturer'].choices = [(asset.module_type.manufacturer.pk, asset.module_type.manufacturer)]
            self.fields['module_type'].widget = StaticSelect(attrs={'readonly':True, 'disabled':True})
            self.fields['module_type'].choices = [(asset.module_type.pk, asset.module_type)]
            self.fields['module_type'].required = False

    def clean_module_type(self):
        return self.instance.assigned_asset.module_type


class AssetCreateInventoryItemForm(InventoryItemForm):
    """
        Populates and disables editing of asset and *_type fields
    """
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

    def clean_manufacturer(self):
        return self.instance.assigned_asset.inventoryitem_type.manufacturer
