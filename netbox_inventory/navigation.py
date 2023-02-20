from packaging import version

from django.conf import settings
from extras.plugins import PluginMenuItem, PluginMenu, PluginMenuButton
from utilities.choices import ButtonColorChoices


asset_buttons = [
    PluginMenuButton(
        link='plugins:netbox_inventory:asset_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        color=ButtonColorChoices.GREEN
    ),
    PluginMenuButton(
        link='plugins:netbox_inventory:asset_import',
        title='Import',
        icon_class='mdi mdi-upload',
        color=ButtonColorChoices.CYAN,
    )
]

supplier_buttons = [
    PluginMenuButton(
        link='plugins:netbox_inventory:supplier_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        color=ButtonColorChoices.GREEN
    ),
    # PluginMenuButton(
    #     link='plugins:netbox_inventory:asset_import',
    #     title='Import',
    #     icon_class='mdi mdi-upload',
    #     color=ButtonColorChoices.CYAN,
    # )
]

purchase_buttons = [
    PluginMenuButton(
        link='plugins:netbox_inventory:purchase_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        color=ButtonColorChoices.GREEN
    ),
    # PluginMenuButton(
    #     link='plugins:netbox_inventory:purchase_import',
    #     title='Import',
    #     icon_class='mdi mdi-upload',
    #     color=ButtonColorChoices.CYAN,
    # )
]

inventoryitemtype_buttons = [
    PluginMenuButton(
        link='plugins:netbox_inventory:inventoryitemtype_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        color=ButtonColorChoices.GREEN
    ),
    # PluginMenuButton(
    #     link='plugins:netbox_inventory:asset_import',
    #     title='Import',
    #     icon_class='mdi mdi-upload',
    #     color=ButtonColorChoices.CYAN,
    # )
]

inventoryitemgroup_buttons = [
    PluginMenuButton(
        link='plugins:netbox_inventory:inventoryitemgroup_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        color=ButtonColorChoices.GREEN
    ),
]

menu_buttons = (
    PluginMenuItem(
        link='plugins:netbox_inventory:asset_list',
        link_text='Assets',
        permissions=["netbox_inventory.view_asset"],
        buttons=asset_buttons,
    ),
    PluginMenuItem(
        link='plugins:netbox_inventory:supplier_list',
        link_text='Suppliers',
        permissions=["netbox_inventory.view_supplier"],
        buttons=supplier_buttons,
    ),
    PluginMenuItem(
        link='plugins:netbox_inventory:purchase_list',
        link_text='Purchases',
        permissions=["netbox_inventory.view_purchase"],
        buttons=purchase_buttons,
    ),
    PluginMenuItem(
        link='plugins:netbox_inventory:inventoryitemtype_list',
        link_text='Inventory Item Types',
        permissions=["netbox_inventory.view_inventoryitemtype"],
        buttons=inventoryitemtype_buttons,
    ),
    PluginMenuItem(
        link='plugins:netbox_inventory:inventoryitemgroup_list',
        link_text='Inventory Item Groups',
        permissions=["netbox_inventory.view_inventoryitemgroup"],
        buttons=inventoryitemgroup_buttons,
    ),
)

current_version = version.parse(settings.VERSION)
REQUIRED_VERSION = version.Version('3.4')
# can't use utils.get_plugin_setting() here, get value manually
if (current_version >= REQUIRED_VERSION and settings.PLUGINS_CONFIG['netbox_inventory']['top_level_menu']):
    # add a top level entry
    menu = PluginMenu(
        label=f'Inventory',
        groups=(
            ('Asset Management', menu_buttons),
        ),
        icon_class='mdi mdi-clipboard-text-multiple-outline'
    )
else:
    # display under plugins
    menu_items = menu_buttons
