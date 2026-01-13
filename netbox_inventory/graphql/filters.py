import strawberry_django

from netbox.graphql.filters import BaseModelFilter

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
class AssetFilter(BaseModelFilter):
    pass


@strawberry_django.filter(models.Supplier, lookups=True)
class SupplierFilter(BaseModelFilter):
    pass


@strawberry_django.filter(models.Purchase, lookups=True)
class PurchaseFilter(BaseModelFilter):
    pass


@strawberry_django.filter(models.Delivery, lookups=True)
class DeliveryFilter(BaseModelFilter):
    pass


@strawberry_django.filter(models.InventoryItemType, lookups=True)
class InventoryItemTypeFilter(BaseModelFilter):
    pass


@strawberry_django.filter(models.InventoryItemGroup, lookups=True)
class InventoryItemGroupFilter(BaseModelFilter):
    pass
