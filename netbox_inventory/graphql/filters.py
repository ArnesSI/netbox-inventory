import strawberry_django
from strawberry import auto

from netbox.graphql.filter_mixins import BaseFilterMixin

from netbox_inventory.models import (
    Asset,
    Contract,
    Delivery,
    InventoryItemGroup,
    InventoryItemType,
    Purchase,
    Supplier,
)

__all__ = (
    'AssetFilter',
    'ContractFilter',
    'DeliveryFilter',
    'InventoryItemGroupFilter',
    'InventoryItemTypeFilter',
    'PurchaseFilter',
    'SupplierFilter',
)


@strawberry_django.filter(Asset)
class AssetFilter(BaseFilterMixin):
    asset_tag: auto
    serial: auto
    name: auto
    status: auto
    tenant_id: auto
    tenant: auto
    device_id: auto
    device: auto
    owner_id: auto
    owner: auto


@strawberry_django.filter(Contract)
class ContractFilter(BaseFilterMixin):
    name: auto
    contract_id: auto
    supplier_id: auto
    supplier: auto
    contract_type: auto
    status: auto
    start_date: auto
    end_date: auto


@strawberry_django.filter(Delivery)
class DeliveryFilter(BaseFilterMixin):
    name: auto
    date: auto
    receiving_contact_id: auto
    receiving_contact: auto


@strawberry_django.filter(InventoryItemGroup)
class InventoryItemGroupFilter(BaseFilterMixin):
    name: auto
    description: auto
    parent_id: auto
    parent: auto


@strawberry_django.filter(InventoryItemType)
class InventoryItemTypeFilter(BaseFilterMixin):
    name: auto
    model: auto
    part_number: auto
    manufacturer_id: auto
    manufacturer: auto
    inventoryitem_group_id: auto
    inventoryitem_group: auto


@strawberry_django.filter(Purchase)
class PurchaseFilter(BaseFilterMixin):
    name: auto
    date: auto
    supplier_id: auto
    supplier: auto


@strawberry_django.filter(Supplier)
class SupplierFilter(BaseFilterMixin):
    name: auto
    description: auto
