import strawberry
import strawberry_django

from .types import (
    AssetType,
    AssetTypeType,
    DeliveryType,
    HardwareType,
    InventoryType,
    InventoryItemGroupType,
    InventoryItemTypeType,
    PurchaseType,
    SupplierType,
)
from netbox_inventory.models import (
    Asset,
    AssetType as AssetTypeModel,
    Delivery,
    Hardware,
    Inventory,
    InventoryItemGroup,
    InventoryItemType,
    Purchase,
    Supplier,
)


@strawberry.type
class AssetQuery:
    @strawberry.field
    def asset(self, id: int) -> AssetType:
        return Asset.objects.get(pk=id)

    asset_list: list[AssetType] = strawberry_django.field()


@strawberry.type
class AssetTypeQuery:
    @strawberry.field
    def asset_type(self, id: int) -> AssetTypeType:
        return AssetTypeModel.objects.get(pk=id)

    asset_type_list: list[AssetTypeType] = strawberry_django.field()


@strawberry.type
class HardwareQuery:
    @strawberry.field
    def hardware(self, id: int) -> HardwareType:
        return Hardware.objects.get(pk=id)

    hardware_list: list[HardwareType] = strawberry_django.field()


@strawberry.type
class InventoryQuery:
    @strawberry.field
    def inventory(self, id: int) -> InventoryType:
        return Inventory.objects.get(pk=id)

    inventory_list: list[InventoryType] = strawberry_django.field()


@strawberry.type
class SupplierQuery:
    @strawberry.field
    def supplier(self, id: int) -> SupplierType:
        return Supplier.objects.get(pk=id)

    supplier_list: list[SupplierType] = strawberry_django.field()


@strawberry.type
class PurchaseQuery:
    @strawberry.field
    def purchase(self, id: int) -> PurchaseType:
        return Purchase.objects.get(pk=id)

    purchase_list: list[PurchaseType] = strawberry_django.field()


@strawberry.type
class DeliveryQuery:
    @strawberry.field
    def delivery(self, id: int) -> DeliveryType:
        return Delivery.objects.get(pk=id)

    delivery_list: list[DeliveryType] = strawberry_django.field()


@strawberry.type
class InventoryItemTypeQuery:
    @strawberry.field
    def inventory_item_type(self, id: int) -> InventoryItemTypeType:
        return InventoryItemType.objects.get(pk=id)

    inventory_item_type_list: list[InventoryItemTypeType] = strawberry_django.field()


@strawberry.type
class InventoryItemGroupQuery:
    @strawberry.field
    def inventory_item_group(self, id: int) -> InventoryItemGroupType:
        return InventoryItemGroup.objects.get(pk=id)

    inventory_item_group_list: list[InventoryItemGroupType] = strawberry_django.field()


schema = [
    AssetQuery,
    AssetTypeQuery,
    HardwareQuery,
    InventoryQuery,
    SupplierQuery,
    PurchaseQuery,
    DeliveryQuery,
    InventoryItemTypeQuery,
    InventoryItemGroupQuery,
]
