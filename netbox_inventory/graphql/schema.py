import strawberry
import strawberry_django

from .types import (
    AssetRoleType,
    AssetType,
    DeliveryType,
    InventoryItemGroupType,
    InventoryItemTypeType,
    PurchaseType,
    SupplierType,
)


@strawberry.type(name='Query')
class AssetQuery:
    asset: AssetType = strawberry_django.field()
    asset_list: list[AssetType] = strawberry_django.field()


@strawberry.type(name='Query')
class AssetRoleQuery:
    asset_role: AssetRoleType = strawberry_django.field()
    asset_role_list: list[AssetRoleType] = strawberry_django.field()


@strawberry.type(name='Query')
class SupplierQuery:
    supplier: SupplierType = strawberry_django.field()
    supplier_list: list[SupplierType] = strawberry_django.field()


@strawberry.type(name='Query')
class PurchaseQuery:
    purchase: PurchaseType = strawberry_django.field()
    purchase_list: list[PurchaseType] = strawberry_django.field()


@strawberry.type(name='Query')
class DeliveryQuery:
    delivery: DeliveryType = strawberry_django.field()
    delivery_list: list[DeliveryType] = strawberry_django.field()


@strawberry.type(name='Query')
class InventoryItemTypeQuery:
    inventory_item_type: InventoryItemTypeType = strawberry_django.field()
    inventory_item_type_list: list[InventoryItemTypeType] = strawberry_django.field()


@strawberry.type(name='Query')
class InventoryItemGroupQuery:
    inventory_item_group: InventoryItemGroupType = strawberry_django.field()
    inventory_item_group_list: list[InventoryItemGroupType] = strawberry_django.field()
