import strawberry
import strawberry_django

import netbox_inventory.models as models
from .types import AssetType, SupplierType, PurchaseType, DeliveryType, InventoryItemTypeType, InventoryItemGroupType

@strawberry.type
class AssetQuery:
    @strawberry.field
    def asset(self, id: int) -> AssetType:
        return models.Asset.get(pk=id)
    asset_list: list[AssetType] = strawberry_django.field()

@strawberry.type
class SupplierQuery:
    @strawberry.field
    def supplier(self, id: int) -> SupplierType:
        return models.Supplier.get(pk=id)
    supplier_list: list[SupplierType] = strawberry_django.field()

@strawberry.type
class PurchaseQuery:
    @strawberry.field
    def purchase(self, id: int) -> PurchaseType:
        return models.Purchase.get(pk=id)
    purchase_list: list[PurchaseType] = strawberry_django.field()

@strawberry.type
class DeliveryQuery:
    @strawberry.field
    def delivery(self, id: int) -> DeliveryType:
        return models.Delivery.get(pk=id)
    delivery_list: list[DeliveryType] = strawberry_django.field()

@strawberry.type
class InventoryItemTypeQuery:
    @strawberry.field
    def inventory_item_type(self, id: int) -> InventoryItemTypeType:
        return models.InventoryItemType.get(pk=id)
    inventory_item_type_list: list[InventoryItemTypeType] = strawberry_django.field()

@strawberry.type
class InventoryItemGroupQuery:
    @strawberry.field
    def inventory_item_group(self, id: int) -> InventoryItemGroupType:
        return models.InventoryItemGroup.get(pk=id)
    inventory_item_group_list: list[InventoryItemGroupType] = strawberry_django.field()
