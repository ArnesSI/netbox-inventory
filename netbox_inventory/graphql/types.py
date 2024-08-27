import strawberry
import strawberry_django
from typing import Annotated

from netbox_inventory.models import Asset, Supplier, Purchase, Delivery, InventoryItemType, InventoryItemGroup

from .filters import (
    AssetFilter,
    SupplierFilter,
    PurchaseFilter,
    DeliveryFilter,
    InventoryItemTypeFilter,
    # InventoryItemGroupFilter
)


@strawberry_django.type(Asset, fields="__all__", filters=AssetFilter)
class AssetType:
    # TODO: Fill in fields
    pass

@strawberry_django.type(Supplier, fields="__all__", filters=SupplierFilter)
class SupplierType:
    # TODO: Fill in fields
    pass

@strawberry_django.type(Purchase, fields="__all__", filters=PurchaseFilter)
class PurchaseType:
    # TODO: Fill in fields
    pass

@strawberry_django.type(Delivery, fields="__all__", filters=DeliveryFilter)
class DeliveryType:
    # Add any custom fields or methods here if needed
    pass

@strawberry_django.type(InventoryItemType, fields="__all__", filters=InventoryItemTypeFilter)
class InventoryItemTypeType:
    # TODO: Fill in fields
    pass

# @strawberry_django.type(InventoryItemGroup, fields="__all__", filters=InventoryItemGroupFilter)
# class InventoryItemGroupType:
#     # TODO: Fill in fields
#     pass
