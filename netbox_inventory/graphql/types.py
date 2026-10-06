from typing import Annotated

import strawberry
import strawberry_django

from dcim.graphql.types import (
    DeviceType,
    DeviceTypeType,
    LocationType,
    ManufacturerType,
    ModuleType,
    ModuleTypeType,
    RackType,
    RackTypeType,
)
from extras.graphql.mixins import ContactsMixin, ImageAttachmentsMixin
from netbox.graphql.types import OrganizationalObjectType, PrimaryObjectType
from tenancy.graphql.types import ContactType, TenantType

from .filters import (
    AssetFilter,
    AssetRoleFilter,
    DeliveryFilter,
    InventoryItemGroupFilter,
    InventoryItemTypeFilter,
    PurchaseFilter,
    SupplierFilter,
)
from netbox_inventory.models import (
    Asset,
    AssetRole,
    Delivery,
    InventoryItemGroup,
    InventoryItemType,
    Purchase,
    Supplier,
)


@strawberry_django.type(Asset, fields='__all__', filters=AssetFilter)
class AssetType(ContactsMixin, ImageAttachmentsMixin, PrimaryObjectType):
    device_type: (
        Annotated['DeviceTypeType', strawberry.lazy('dcim.graphql.types')] | None
    )
    module_type: (
        Annotated['ModuleTypeType', strawberry.lazy('dcim.graphql.types')] | None
    )
    inventoryitem_type: (
        Annotated[
            'InventoryItemTypeType', strawberry.lazy('netbox_inventory.graphql.types')
        ]
        | None
    )
    rack_type: Annotated['RackTypeType', strawberry.lazy('dcim.graphql.types')] | None
    tenant: Annotated['TenantType', strawberry.lazy('tenancy.graphql.types')] | None
    device: Annotated['DeviceType', strawberry.lazy('dcim.graphql.types')] | None
    module: Annotated['ModuleType', strawberry.lazy('dcim.graphql.types')] | None
    inventoryitem: (
        Annotated['InventoryItemType', strawberry.lazy('dcim.graphql.types')] | None
    )
    rack: Annotated['RackType', strawberry.lazy('dcim.graphql.types')] | None
    storage_location: (
        Annotated['LocationType', strawberry.lazy('dcim.graphql.types')] | None
    )
    owning_tenant: (
        Annotated['TenantType', strawberry.lazy('tenancy.graphql.types')] | None
    )
    role: (
        Annotated['AssetRoleType', strawberry.lazy('netbox_inventory.graphql.types')]
        | None
    )
    delivery: (
        Annotated['DeliveryType', strawberry.lazy('netbox_inventory.graphql.types')]
        | None
    )
    purchase: (
        Annotated['PurchaseType', strawberry.lazy('netbox_inventory.graphql.types')]
        | None
    )

@strawberry_django.type(
    AssetRole, fields='__all__', filters=AssetRoleFilter
)
class AssetRoleType(OrganizationalObjectType):
    color: str
    parent: (
        Annotated[
            'AssetRoleType', strawberry.lazy('netbox_inventory.graphql.types')
        ]
        | None
    )
    children: list[
        Annotated[
            'AssetRoleType', strawberry.lazy('netbox_inventory.graphql.types')
        ]
    ]

@strawberry_django.type(Supplier, fields='__all__', filters=SupplierFilter)
class SupplierType(ContactsMixin, PrimaryObjectType):
    purchases: list[
        Annotated['PurchaseType', strawberry.lazy('netbox_inventory.graphql.types')]
    ]


@strawberry_django.type(Purchase, fields='__all__', filters=PurchaseFilter)
class PurchaseType(PrimaryObjectType):
    supplier: Annotated[
        'SupplierType', strawberry.lazy('netbox_inventory.graphql.types')
    ]
    assets: list[
        Annotated['AssetType', strawberry.lazy('netbox_inventory.graphql.types')]
    ]
    orders: list[
        Annotated['DeliveryType', strawberry.lazy('netbox_inventory.graphql.types')]
    ]


@strawberry_django.type(Delivery, fields='__all__', filters=DeliveryFilter)
class DeliveryType(PrimaryObjectType):
    purchase: Annotated[
        'PurchaseType', strawberry.lazy('netbox_inventory.graphql.types')
    ]
    receiving_contact: (
        Annotated['ContactType', strawberry.lazy('tenancy.graphql.types')] | None
    )
    assets: list[
        Annotated['AssetType', strawberry.lazy('netbox_inventory.graphql.types')]
    ]


@strawberry_django.type(
    InventoryItemType, fields='__all__', filters=InventoryItemTypeFilter
)
class InventoryItemTypeType(ImageAttachmentsMixin, PrimaryObjectType):
    manufacturer: Annotated['ManufacturerType', strawberry.lazy('dcim.graphql.types')]
    inventoryitem_group: (
        Annotated[
            'InventoryItemGroupType', strawberry.lazy('netbox_inventory.graphql.types')
        ]
        | None
    )


@strawberry_django.type(
    InventoryItemGroup, fields='__all__', filters=InventoryItemGroupFilter
)
class InventoryItemGroupType(OrganizationalObjectType):
    parent: (
        Annotated[
            'InventoryItemGroupType', strawberry.lazy('netbox_inventory.graphql.types')
        ]
        | None
    )
    inventoryitem_types: list[
        Annotated[
            'InventoryItemTypeType', strawberry.lazy('netbox_inventory.graphql.types')
        ]
    ]
    children: list[
        Annotated[
            'InventoryItemGroupType', strawberry.lazy('netbox_inventory.graphql.types')
        ]
    ]
