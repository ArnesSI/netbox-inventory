from netbox.search import SearchIndex
from .models import Asset, InventoryItemType, InventoryItemGroup, Purchase, Supplier


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


indexes = [
    AssetIndex,
    SupplierIndex,
    PurchaseIndex,
    InventoryItemTypeIndex,
    InventoryItemGroupIndex,
]
