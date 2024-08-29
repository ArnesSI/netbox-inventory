import strawberry_django

from netbox.graphql.filter_mixins import autotype_decorator, BaseFilterMixin

from netbox_inventory import filtersets, models

__all__ = (
    "AssetFilter",
    "SupplierFilter",
    "PurchaseFilter",
    "DeliveryFilter",
    "InventoryItemTypeFilter",
    "InventoryItemGroupFilter",
)


@strawberry_django.filter(models.Asset, lookups=True)
@autotype_decorator(filtersets.AssetFilterSet)
class AssetFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Supplier, lookups=True)
@autotype_decorator(filtersets.SupplierFilterSet)
class SupplierFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Purchase, lookups=True)
@autotype_decorator(filtersets.PurchaseFilterSet)
class PurchaseFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.Delivery, lookups=True)
@autotype_decorator(filtersets.DeliveryFilterSet)
class DeliveryFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.InventoryItemType, lookups=True)
@autotype_decorator(filtersets.InventoryItemTypeFilterSet)
class InventoryItemTypeFilter(BaseFilterMixin):
    pass


@strawberry_django.filter(models.InventoryItemGroup, lookups=True)
@autotype_decorator(filtersets.InventoryItemGroupFilterSet)
class InventoryItemGroupFilter(BaseFilterMixin):
    pass
