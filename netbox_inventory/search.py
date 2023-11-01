from netbox.search import SearchIndex
from .models import Asset, Delivery, InventoryItemType, InventoryItemGroup, Purchase, Supplier, ConsumableType, Consumable


class AssetIndex(SearchIndex):
    model = Asset
    fields = (
        ("name", 100),
        ("asset_tag", 50),
        ("serial", 60),
        ("comments", 5000),
    )


class SupplierIndex(SearchIndex):
    model = Supplier
    fields = (
        ("name", 100),
        ("description", 500),
        ("comments", 5000),
    )


class PurchaseIndex(SearchIndex):
    model = Purchase
    fields = (
        ("name", 100),
        ("description", 500),
        ("comments", 5000),
    )


class DeliveryIndex(SearchIndex):
    model = Delivery
    fields = (
        ("name", 100),
        ("description", 500),
        ("comments", 5000),
    )


class InventoryItemTypeIndex(SearchIndex):
    model = InventoryItemType
    fields = (
        ("model", 100),
        ("part_number", 100),
        ("comments", 5000),
    )


class InventoryItemGroupIndex(SearchIndex):
    model = InventoryItemGroup
    fields = (
        ("name", 100),
        ("comments", 5000),
    )

class ConsumableTypeIndex(SearchIndex):
    model = ConsumableType
    fields = (
        ("name", 100),
        ("part_number", 100),
        ("comments", 5000),
    )

class ConsumableIndex(SearchIndex):
    model = Consumable
    fields = (
        ("consumable_type", 100),
        ("storage_location", 1000),
        ("comments", 5000),
    )

indexes = [
    AssetIndex,
    SupplierIndex,
    PurchaseIndex,
    DeliveryIndex,
    InventoryItemTypeIndex,
    InventoryItemGroupIndex,
    ConsumableTypeIndex,
    ConsumableIndex,
]
