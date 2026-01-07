import strawberry_django

from netbox.graphql.filters import PrimaryModelFilter, NestedGroupModelFilter

from netbox_inventory import models

__all__ = (
    'AssetFilter',
    'SupplierFilter',
    'PurchaseFilter',
    'DeliveryFilter',
    'InventoryItemTypeFilter',
    'InventoryItemGroupFilter',
)


@strawberry_django.filter(models.Asset, lookups=True)
class AssetFilter(PrimaryModelFilter):
    pass


@strawberry_django.filter(models.Supplier, lookups=True)
class SupplierFilter(PrimaryModelFilter):
    pass


@strawberry_django.filter(models.Purchase, lookups=True)
class PurchaseFilter(PrimaryModelFilter):
    pass


@strawberry_django.filter(models.Delivery, lookups=True)
class DeliveryFilter(PrimaryModelFilter):
    pass


@strawberry_django.filter(models.InventoryItemType, lookups=True)
class InventoryItemTypeFilter(PrimaryModelFilter):
    pass


@strawberry_django.filter(models.InventoryItemGroup, lookups=True)
class InventoryItemGroupFilter(NestedGroupModelFilter):
    pass
