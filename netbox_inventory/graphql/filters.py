import strawberry_django
from netbox.graphql.filter_mixins import BaseFilterMixin

from netbox_inventory import filtersets, models

__all__ = (
    'AssetFilter',
    'SupplierFilter',
    'PurchaseFilter',
    'DeliveryFilter',
    'InventoryItemTypeFilter',
    'InventoryItemGroupFilter',
)


@strawberry_django.filter(models.Asset, lookups=True)
class AssetFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Supplier, lookups=True)
class SupplierFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Purchase, lookups=True)
class PurchaseFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Delivery, lookups=True)
class DeliveryFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.InventoryItemType, lookups=True)
class InventoryItemTypeFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.InventoryItemGroup, lookups=True)
class InventoryItemGroupFilter(BaseFilterMixin):
    pass
