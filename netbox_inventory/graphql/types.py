import strawberry
import strawberry_django
from typing import Annotated
from extras.graphql.mixins import ContactsMixin, ImageAttachmentsMixin
from netbox.graphql.types import (
    NetBoxObjectType,
    OrganizationalObjectType,
)
from netbox_inventory.models import (
    Asset,
    Supplier,
    Purchase,
    Delivery,
    InventoryItemType,
    InventoryItemGroup,
)
from .filters import (
    AssetFilter,
    SupplierFilter,
    PurchaseFilter,
    DeliveryFilter,
    InventoryItemTypeFilter,
    InventoryItemGroupFilter,
)


@strawberry_django.type(Asset, fields="__all__", filters=AssetFilter)
class AssetType(ImageAttachmentsMixin, NetBoxObjectType):
    device_type: (
        Annotated["DeviceTypeType", strawberry.lazy("dcim.graphql.types")] | None
    )
    module_type: (
        Annotated["ModuleTypeType", strawberry.lazy("dcim.graphql.types")] | None
    )
    inventoryitem_type: (
        Annotated[
            "InventoryItemTypeType", strawberry.lazy("netbox_inventory.graphql.types")
        ]
        | None
    )
    tenant: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None
    device: Annotated["DeviceType", strawberry.lazy("dcim.graphql.types")] | None
    module: Annotated["ModuleType", strawberry.lazy("dcim.graphql.types")] | None
    contact: Annotated["ContactType", strawberry.lazy("tenancy.graphql.types")] | None
    inventoryitem: (
        Annotated["InventoryItemType", strawberry.lazy("dcim.graphql.types")] | None
    )
    storage_location: (
        Annotated["LocationType", strawberry.lazy("dcim.graphql.types")] | None
    )
    owner: Annotated["TenantType", strawberry.lazy("tenancy.graphql.types")] | None
    delivery: (
        Annotated["DeliveryType", strawberry.lazy("netbox_inventory.graphql.types")]
        | None
    )
    purchase: (
        Annotated["PurchaseType", strawberry.lazy("netbox_inventory.graphql.types")]
        | None
    )


@strawberry_django.type(Supplier, fields="__all__", filters=SupplierFilter)
class SupplierType(ContactsMixin, NetBoxObjectType):
    purchases: list[
        Annotated["PurchaseType", strawberry.lazy("netbox_inventory.graphql.types")]
    ]


@strawberry_django.type(Purchase, fields="__all__", filters=PurchaseFilter)
class PurchaseType(NetBoxObjectType):
    supplier: Annotated[
        "SupplierType", strawberry.lazy("netbox_inventory.graphql.types")
    ]
    assets: list[
        Annotated["AssetType", strawberry.lazy("netbox_inventory.graphql.types")]
    ]
    orders: list[
        Annotated["DeliveryType", strawberry.lazy("netbox_inventory.graphql.types")]
    ]


@strawberry_django.type(Delivery, fields="__all__", filters=DeliveryFilter)
class DeliveryType(NetBoxObjectType):
    purchase: Annotated[
        "PurchaseType", strawberry.lazy("netbox_inventory.graphql.types")
    ]
    receiving_contact: (
        Annotated["ContactType", strawberry.lazy("tenancy.graphql.types")] | None
    )
    assets: list[
        Annotated["AssetType", strawberry.lazy("netbox_inventory.graphql.types")]
    ]


@strawberry_django.type(
    InventoryItemType, fields="__all__", filters=InventoryItemTypeFilter
)
class InventoryItemTypeType(ImageAttachmentsMixin, NetBoxObjectType):
    manufacturer: Annotated["ManufacturerType", strawberry.lazy("dcim.graphql.types")]
    inventoryitem_group: (
        Annotated[
            "InventoryItemGroupType", strawberry.lazy("netbox_inventory.graphql.types")
        ]
        | None
    )


@strawberry_django.type(
    InventoryItemGroup, fields="__all__", filters=InventoryItemGroupFilter
)
class InventoryItemGroupType(OrganizationalObjectType):
    parent: (
        Annotated[
            "InventoryItemGroupType", strawberry.lazy("netbox_inventory.graphql.types")
        ]
        | None
    )
    inventoryitem_types: list[
        Annotated[
            "InventoryItemTypeType", strawberry.lazy("netbox_inventory.graphql.types")
        ]
    ]
    children: list[
        Annotated[
            "InventoryItemGroupType", strawberry.lazy("netbox_inventory.graphql.types")
        ]
    ]
