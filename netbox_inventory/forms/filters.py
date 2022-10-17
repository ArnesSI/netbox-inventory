from cProfile import label
from dcim.models import DeviceType, Manufacturer, ModuleType
from netbox.forms import NetBoxModelFilterSetForm
from utilities.forms import (
    DynamicModelMultipleChoiceField, MultipleChoiceField, TagFilterField
)
from ..choices import InventoryStatusChoices
from ..models import Asset, InventoryItemType, Purchase, Supplier


__all__ = (
    'AssetFilterForm',
    'SupplierFilterForm',
    'PurchaseFilterForm',
)


class AssetFilterForm(NetBoxModelFilterSetForm):
    model = Asset

    status = MultipleChoiceField(
        choices=InventoryStatusChoices,
        required=False,
    )
    manufacturer = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
    )
    device_type = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer',
        },
    )
    module_type = DynamicModelMultipleChoiceField(
        queryset=ModuleType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer',
        },
    )
    inventoryitem_type_id = DynamicModelMultipleChoiceField(
        queryset=InventoryItemType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer',
        },
        label='Inventory item type'
    )
    supplier_id = DynamicModelMultipleChoiceField(
        queryset=Supplier.objects.all(),
        required=False,
        label='Supplier',
    )


class SupplierFilterForm(NetBoxModelFilterSetForm):
    model = Supplier
    tag = TagFilterField(model)


class PurchaseFilterForm(NetBoxModelFilterSetForm):
    model = Purchase
    tag = TagFilterField(model)
