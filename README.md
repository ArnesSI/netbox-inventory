## netbox-inventory

Manage your hardware inventory in NetBox.

### Features

Keep track of your hardware, whether it is installed or in storage. You can
define assets that represent hardware that can be used as a device, module or
inventory item in NetBox.

Each asset can have a storage location defined, when not in use. You can assign
an asset to a device or module. The plugin can keep serial number and asset tag
between asset and device or module in sync if enabled in settings.

To properly support inventory items (that are used in NetBox to model SFP and
similar modules) the plugin defines inventory item types that are equivalent to
device types and module types.


### Automatic management of asset status

Each asset has a status attribute that can indicate use of the asset. These
statuses can be set as needed by each NetBox installation. 

Two statuses can have a special meaning. One to indicate asset is in storage and one
to indicate asset is in use. 

netbox_inventory can automatically set status to the value specified in
`used_status_name` configuration item when an asset is assigned to a device, module
or inventory item.

When you remove an asset from device, module or inventory item the plugin will set
asset status to `stored_status_name` configuration item.

To disable automatically changing status, set these two config parameters to `None`.

### Settings

| Setting | Default value | Description |
|---------|---------------|-------------|
| `used_status_name` | `'used'`| Status that indicates asset is in use. See "Automatic management of asset status" below for more info on this setting.
| `stored_status_name` | `'stored'`| Status that indicates asset is in storage. See "Automatic management of asset status" below for more info on this setting.
| `sync_hardware_serial_asset_tag` | `False` | When an asset is assigned or unassigned to a device, module or inventory item, update its serial number and asset tag to be in sync with the asset? |
| `asset_import_create_supplier` | `False` | When importing assets, automatically create supplier if it doesn't exist |
| `asset_import_create_device_type` | `False` | When importing a device type asset, automatically create manufacturer and/or device type if it doesn't exist |
| `asset_import_create_module_type` | `False` | When importing a module type asset, automatically create manufacturer and/or device type if it doesn't exist |
| `asset_import_create_inventoryitem_type` | `False` | When importing an inventory type asset, automatically create manufacturer and/or device type if it doesn't exist |


### Future development ideas

- add option to lock editing certain Asset fields if asset has certain tag. also prevent Asset delete
- location report
- supplier detail - show assets
- device on_delete update asset.status (if asset assigned)
- prevent device.device_type/serial/asset_tag change if asset assigned (and sync_hardware_serial_asset_tag=true?) see [AbortRequest](https://github.com/netbox-community/netbox/issues/9075)
- inject asset list on manufacturer detail?
- inventoryitem detail - show asset info
- inventoryitem_type - assign existing, bulk, show assets, more testing
- bootstrap scripts to generate assets from existing device/module S/N data
- from device details view -> to change asset, assign asset
- supplier import, bulk edit
- how to assign MACs to device/module interfaces that is created from Asset
