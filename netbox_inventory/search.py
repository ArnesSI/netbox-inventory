from netbox.search import SearchIndex

from .models import (
    Asset,
    AuditTrailSource,
    Delivery,
    InventoryItemGroup,
    InventoryItemType,
    Purchase,
    Supplier,
)

#
# Assets
#


class InventoryItemGroupIndex(SearchIndex):
    model = InventoryItemGroup
    fields = (
        ('name', 100),
        ('description', 500),
        ('comments', 5000),
    )


class InventoryItemTypeIndex(SearchIndex):
    model = InventoryItemType
    fields = (
        ('model', 100),
        ('part_number', 100),
        ('description', 500),
        ('comments', 5000),
    )


class AssetIndex(SearchIndex):
    model = Asset
    fields = (
        ('name', 100),
        ('asset_tag', 50),
        ('serial', 60),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('name', 'asset_tag', 'status')


#
# Deliveries
#


class SupplierIndex(SearchIndex):
    model = Supplier
    fields = (
        ('name', 100),
        ('description', 500),
        ('comments', 5000),
    )


class PurchaseIndex(SearchIndex):
    model = Purchase
    fields = (
        ('name', 100),
        ('description', 500),
        ('comments', 5000),
    )


class DeliveryIndex(SearchIndex):
    model = Delivery
    fields = (
        ('name', 100),
        ('description', 500),
        ('comments', 5000),
    )


#
# Audit
#


class AuditTrailSourceIndex(SearchIndex):
    model = AuditTrailSource
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
        ('comments', 5000),
    )


indexes = [
    InventoryItemGroupIndex,
    InventoryItemTypeIndex,
    AssetIndex,
    SupplierIndex,
    PurchaseIndex,
    DeliveryIndex,
    AuditTrailSourceIndex,
]
