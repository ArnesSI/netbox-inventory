from netbox.plugins import (
    PluginMenu,
    PluginMenuButton,
    PluginMenuItem,
    get_plugin_config,
)

#
# Assets
#

inventoryitemgroup_buttons = [
    PluginMenuButton(
        link='plugins:netbox_inventory:inventoryitemgroup_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        permissions=['netbox_inventory.add_inventoryitemgroup'],
    ),
    PluginMenuButton(
        link='plugins:netbox_inventory:inventoryitemgroup_bulk_import',
        title='Import',
        icon_class='mdi mdi-upload',
        permissions=['netbox_inventory.add_inventoryitemgroup'],
    ),
]

inventoryitemtype_buttons = [
    PluginMenuButton(
        link='plugins:netbox_inventory:inventoryitemtype_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        permissions=['netbox_inventory.add_inventoryitemtype'],
    ),
    PluginMenuButton(
        link='plugins:netbox_inventory:inventoryitemtype_bulk_import',
        title='Import',
        icon_class='mdi mdi-upload',
        permissions=['netbox_inventory.add_inventoryitemtype'],
    ),
]

asset_buttons = [
    PluginMenuButton(
        link='plugins:netbox_inventory:asset_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        permissions=['netbox_inventory.add_asset'],
    ),
    PluginMenuButton(
        link='plugins:netbox_inventory:asset_bulk_import',
        title='Import',
        icon_class='mdi mdi-upload',
        permissions=['netbox_inventory.add_asset'],
    ),
]

assets_items = (
    PluginMenuItem(
        link='plugins:netbox_inventory:asset_list',
        link_text='Assets',
        permissions=['netbox_inventory.view_asset'],
        buttons=asset_buttons,
    ),
    PluginMenuItem(
        link='plugins:netbox_inventory:inventoryitemtype_list',
        link_text='Inventory Item Types',
        permissions=['netbox_inventory.view_inventoryitemtype'],
        buttons=inventoryitemtype_buttons,
    ),
    PluginMenuItem(
        link='plugins:netbox_inventory:inventoryitemgroup_list',
        link_text='Inventory Item Groups',
        permissions=['netbox_inventory.view_inventoryitemgroup'],
        buttons=inventoryitemgroup_buttons,
    ),
)


#
# Deliveries
#

supplier_buttons = [
    PluginMenuButton(
        link='plugins:netbox_inventory:supplier_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        permissions=['netbox_inventory.add_supplier'],
    ),
    PluginMenuButton(
        link='plugins:netbox_inventory:supplier_bulk_import',
        title='Import',
        icon_class='mdi mdi-upload',
        permissions=['netbox_inventory.add_supplier'],
    ),
]

purchase_buttons = [
    PluginMenuButton(
        link='plugins:netbox_inventory:purchase_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        permissions=['netbox_inventory.add_purchase'],
    ),
    PluginMenuButton(
        link='plugins:netbox_inventory:purchase_bulk_import',
        title='Import',
        icon_class='mdi mdi-upload',
        permissions=['netbox_inventory.add_purchase'],
    ),
]

delivery_buttons = [
    PluginMenuButton(
        link='plugins:netbox_inventory:delivery_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        permissions=['netbox_inventory.add_delivery'],
    ),
    PluginMenuButton(
        link='plugins:netbox_inventory:delivery_bulk_import',
        title='Import',
        icon_class='mdi mdi-upload',
        permissions=['netbox_inventory.add_delivery'],
    ),
]

deliveries_items = (
    PluginMenuItem(
        link='plugins:netbox_inventory:supplier_list',
        link_text='Suppliers',
        permissions=['netbox_inventory.view_supplier'],
        buttons=supplier_buttons,
    ),
    PluginMenuItem(
        link='plugins:netbox_inventory:purchase_list',
        link_text='Purchases',
        permissions=['netbox_inventory.view_purchase'],
        buttons=purchase_buttons,
    ),
    PluginMenuItem(
        link='plugins:netbox_inventory:delivery_list',
        link_text='Deliveries',
        permissions=['netbox_inventory.view_delivery'],
        buttons=delivery_buttons,
    ),
)


#
# Menu
#

if get_plugin_config('netbox_inventory', 'top_level_menu'):
    # add a top level entry
    menu = PluginMenu(
        label='Inventory',
        groups=(
            ('Asset Management', assets_items),
            ('Deliveries', deliveries_items),
        ),
        icon_class='mdi mdi-clipboard-text-multiple-outline',
    )
else:
    # display under plugins
    menu_items = assets_items + deliveries_items
