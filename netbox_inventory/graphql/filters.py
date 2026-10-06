import strawberry_django
from strawberry_django import StrFilterLookup

from netbox.graphql.filters import BaseModelFilter
from tenancy.graphql.filter_mixins import ContactFilterMixin

from netbox_inventory import models

__all__ = (
    'AssetFilter',
    'AssetRoleFilter',
    'SupplierFilter',
    'PurchaseFilter',
    'DeliveryFilter',
    'InventoryItemTypeFilter',
    'InventoryItemGroupFilter',
)


@strawberry_django.filter(models.Asset, lookups=True)
class AssetFilter(ContactFilterMixin, BaseModelFilter):
    pass

@strawberry_django.filter(models.AssetRole, lookups=True)
class AssetRoleFilter(BaseModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()
    slug: StrFilterLookup | None = strawberry_django.filter_field()

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
