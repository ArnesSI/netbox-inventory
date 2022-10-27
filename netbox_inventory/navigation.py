from extras.plugins import PluginMenuButton, PluginMenuItem
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

menu_items = (
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
)
