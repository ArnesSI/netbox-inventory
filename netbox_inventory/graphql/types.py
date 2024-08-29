import strawberry
import strawberry_django
from typing import Annotated, Optional

from netbox_inventory.models import Asset, Supplier, Purchase, Delivery, InventoryItemType, InventoryItemGroup
from .filters import (
    AssetFilter,
    SupplierFilter,
    PurchaseFilter,
    DeliveryFilter,
    InventoryItemTypeFilter,
    InventoryItemGroupFilter
)

# TODO: Add tags (tried with mixin)
# TODO: Change status to status choices
# TODO: InventoryItemType, i don't see an InventoryItemTypeType in the models
# TODO: DeliveryType
# TODO: PurchaseType


@strawberry_django.type(Asset, fields="__all__", filters=AssetFilter)
class AssetType:
    device_type: Annotated["DeviceTypeType", strawberry.lazy('dcim.graphql.types')] | None
    module_type: Optional[Annotated["ModuleTypeType", strawberry.lazy("dcim.graphql.types")]] | None
    # inventoryitem_type: Optional[Annotated["InventoryItemTypeType", strawberry.lazy("netbox.dcim.graphql.types")]] | None
    tenant: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None
    device: Annotated["DeviceType", strawberry.lazy('dcim.graphql.types')] | None
    module: Annotated["ModuleType", strawberry.lazy('dcim.graphql.types')] | None
    contact: Annotated["ContactType", strawberry.lazy('tenancy.graphql.types')] | None
    inventoryitem: Annotated["InventoryItemType", strawberry.lazy('dcim.graphql.types')] | None
    storage_location: Annotated["LocationType", strawberry.lazy('dcim.graphql.types')] | None
    owner: Annotated["TenantType", strawberry.lazy('tenancy.graphql.types')] | None
    # @strawberry_django.field
    # def device(self) -> Optional[Annotated["DeviceType", strawberry.lazy("netbox.dcim.graphql.types")]]:
    #     return self.device
    #
    # @strawberry_django.field
    # def module(self) -> Optional[Annotated["ModuleType", strawberry.lazy("netbox.dcim.graphql.types")]]:
    #     return self.module
    #
    #

    #
    # @strawberry_django.field
    # def storage_location(self) -> Optional[Annotated["Location", strawberry.lazy("netbox.graphql.types")]]:
    #     return self.storage_location
    #
    # @strawberry_django.field
    # def owner(self) -> Optional[Annotated["Tenant", strawberry.lazy("netbox.graphql.types")]]:
    #     return self.owner
    #
    # @strawberry_django.field
    # def delivery(self) -> Optional[Annotated["DeliveryType", strawberry.lazy("netbox_inventory.graphql.types")]]:
    #     return self.delivery
    #
    # @strawberry_django.field
    # def purchase(self) -> Optional[Annotated["PurchaseType", strawberry.lazy("netbox_inventory.graphql.types")]]:
    #     return self.purchase

@strawberry_django.type(Supplier, fields="__all__", filters=SupplierFilter)
class SupplierType:
    @strawberry_django.field
    def purchases(self) -> list[Annotated["PurchaseType", strawberry.lazy("netbox_inventory.graphql.types")]]:
        return self.purchases.all()

@strawberry_django.type(Purchase, fields="__all__", filters=PurchaseFilter)
class PurchaseType:
    @strawberry_django.field
    def supplier(self) -> Annotated["SupplierType", strawberry.lazy("netbox_inventory.graphql.types")]:
        return self.supplier

    @strawberry_django.field
    def orders(self) -> list[Annotated["DeliveryType", strawberry.lazy("netbox_inventory.graphql.types")]]:
        return self.orders.all()

    @strawberry_django.field
    def assets(self) -> list[Annotated["AssetType", strawberry.lazy("netbox_inventory.graphql.types")]]:
        return self.assets.all()

@strawberry_django.type(Delivery, fields="__all__", filters=DeliveryFilter)
class DeliveryType:
    @strawberry_django.field
    def purchase(self) -> Annotated["PurchaseType", strawberry.lazy("netbox_inventory.graphql.types")]:
        return self.purchase

    @strawberry_django.field
    def receiving_contact(self) -> Optional[Annotated["Contact", strawberry.lazy("netbox.graphql.types")]]:
        return self.receiving_contact

    @strawberry_django.field
    def assets(self) -> list[Annotated["AssetType", strawberry.lazy("netbox_inventory.graphql.types")]]:
        return self.assets.all()

@strawberry_django.type(InventoryItemType, fields="__all__", filters=InventoryItemTypeFilter)
class InventoryItemTypeType:
    @strawberry_django.field
    def manufacturer(self) -> Annotated["Manufacturer", strawberry.lazy("netbox.graphql.types")]:
        return self.manufacturer

    @strawberry_django.field
    def inventoryitem_group(self) -> Optional[
        Annotated["InventoryItemGroupType", strawberry.lazy("netbox_inventory.graphql.types")]]:
        return self.inventoryitem_group

@strawberry_django.type(InventoryItemGroup, fields="__all__", filters=InventoryItemGroupFilter)
class InventoryItemGroupType:
    @strawberry_django.field
    def parent(self) -> Optional[Annotated["InventoryItemGroupType", strawberry.lazy("netbox_inventory.graphql.types")]]:
        return self.parent

    @strawberry_django.field
    def children(self) -> list[Annotated["InventoryItemGroupType", strawberry.lazy("netbox_inventory.graphql.types")]]:
        return self.children.all()

    @strawberry_django.field
    def inventoryitem_types(self) -> list[
        Annotated["InventoryItemTypeType", strawberry.lazy("netbox_inventory.graphql.types")]]:
        return self.inventoryitem_types.all()