import strawberry_django

from netbox.graphql.filter_mixins import autotype_decorator, BaseFilterMixin

from netbox_inventory.models import (
    Asset,
    Supplier,
    Purchase,
    Delivery,
    InventoryItemType,
    # InventoryItemGroup
)

from netbox_inventory.filtersets import (
    AssetFilterSet,
    SupplierFilterSet,
    PurchaseFilterSet,
    DeliveryFilterSet,
    InventoryItemTypeFilterSet,
    # InventoryItemGroupFilterSet
)

__all__ = (
    'AssetFilter',
    'SupplierFilter',
    'PurchaseFilter',
    'DeliveryFilter',
    'InventoryItemTypeFilter',
    # 'InventoryItemGroupFilter',
)

@strawberry_django.filter(Asset, lookups=True)
@autotype_decorator(AssetFilterSet)
class AssetFilter(BaseFilterMixin):
    pass

@strawberry_django.filter(Supplier, lookups=True)
@autotype_decorator(SupplierFilterSet)
class SupplierFilter(BaseFilterMixin):
    pass

@strawberry_django.filter(Purchase, lookups=True)
@autotype_decorator(PurchaseFilterSet)
class PurchaseFilter(BaseFilterMixin):
    pass

@strawberry_django.filter(Delivery, lookups=True)
@autotype_decorator(DeliveryFilterSet)
class DeliveryFilter(BaseFilterMixin):
    pass

@strawberry_django.filter(InventoryItemType, lookups=True)
@autotype_decorator(InventoryItemTypeFilterSet)
class InventoryItemTypeFilter(BaseFilterMixin):
    pass
#
# @strawberry_django.filter(InventoryItemGroup, lookups=True)
# @autotype_decorator(InventoryItemGroupFilterSet)
# class InventoryItemGroupFilter(BaseFilterMixin):
#     pass
#
