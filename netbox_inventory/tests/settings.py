from copy import deepcopy
from django.conf import settings

""" Custom settings to use with override_settings in tests """


CONFIG_ALLOW_CREATE_DEVICE_TYPE = deepcopy(settings.PLUGINS_CONFIG)
CONFIG_ALLOW_CREATE_DEVICE_TYPE['netbox_inventory']['asset_import_create_device_type']=True

CONFIG_SYNC_ON = deepcopy(settings.PLUGINS_CONFIG)
CONFIG_SYNC_ON['netbox_inventory']['sync_hardware_serial_asset_tag']=True

CONFIG_SYNC_OFF = deepcopy(settings.PLUGINS_CONFIG)
CONFIG_SYNC_OFF['netbox_inventory']['sync_hardware_serial_asset_tag']=False