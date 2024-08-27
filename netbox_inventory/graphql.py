import strawberry
import strawberry_django
from typing import Annotated

from .models import (
    Asset,
    Supplier,
    Purchase,
    Delivery,
    InventoryItemType,
    InventoryItemGroup,
)
from .filtersets import (
    AssetFilterSet,
    SupplierFilterSet,
    PurchaseFilterSet,
    DeliveryFilterSet,
    InventoryItemTypeFilterSet,
    InventoryItemGroupFilterSet,
)
from netbox.graphql.filter_mixins import autotype_decorator, BaseFilterMixin

# Filter definitions using existing FilterSets
@strawberry_django.filter(Asset)
@autotype_decorator(AssetFilterSet)
class AssetFilter(BaseFilterMixin):
    pass

@strawberry_django.filter(Supplier)
@autotype_decorator(SupplierFilterSet)
class SupplierFilter(BaseFilterMixin):
    pass

@strawberry_django.filter(Purchase)
@autotype_decorator(PurchaseFilterSet)
class PurchaseFilter(BaseFilterMixin):
    pass

@strawberry_django.filter(Delivery)
@autotype_decorator(DeliveryFilterSet)
class DeliveryFilter(BaseFilterMixin):
    pass

@strawberry_django.filter(InventoryItemType)
@autotype_decorator(InventoryItemTypeFilterSet)
class InventoryItemTypeFilter(BaseFilterMixin):
    pass

@strawberry_django.filter(InventoryItemGroup)
@autotype_decorator(InventoryItemGroupFilterSet)
class InventoryItemGroupFilter(BaseFilterMixin):
    pass

# Type definitions
@strawberry_django.type(Asset, fields="__all__", filters=AssetFilter)
class AssetType:
    pass

@strawberry_django.type(Supplier, fields="__all__", filters=SupplierFilter)
class SupplierType:
    pass

@strawberry_django.type(Purchase, fields="__all__", filters=PurchaseFilter)
class PurchaseType:
    pass

@strawberry_django.type(Delivery, fields="__all__", filters=DeliveryFilter)
class DeliveryType:
    pass

@strawberry_django.type(InventoryItemType, fields="__all__", filters=InventoryItemTypeFilter)
class InventoryItemTypeType:
    pass

@strawberry_django.type(InventoryItemGroup, fields="__all__", filters=InventoryItemGroupFilter)
class InventoryItemGroupType:
    pass

# Query definition
@strawberry.type
class Query:
    asset: AssetType = strawberry_django.field()
    supplier: SupplierType = strawberry_django.field()
    purchase: PurchaseType = strawberry_django.field()
    delivery: DeliveryType = strawberry_django.field()
    inventory_item_type: InventoryItemTypeType = strawberry_django.field()
    inventory_item_group: InventoryItemGroupType = strawberry_django.field()

    asset_list: list[AssetType] = strawberry_django.field()
    supplier_list: list[SupplierType] = strawberry_django.field()
    purchase_list: list[PurchaseType] = strawberry_django.field()
    delivery_list: list[DeliveryType] = strawberry_django.field()
    inventory_item_type_list: list[InventoryItemTypeType] = strawberry_django.field()
    inventory_item_group_list: list[InventoryItemGroupType] = strawberry_django.field()

schema = strawberry.Schema(query=Query)