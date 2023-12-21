from graphene import ObjectType
from netbox.graphql.types import NetBoxObjectType
from netbox.graphql.fields import ObjectField, ObjectListField
from .filtersets import (
    AssetFilterSet,
    SupplierFilterSet,
    PurchaseFilterSet,
    DeliveryFilterSet,
    InventoryItemTypeFilterSet,
    InventoryItemGroupFilterSet,
)
from .models import (
    Asset,
    Supplier,
    Purchase,
    Delivery,
    InventoryItemType,
    InventoryItemGroup,
)


class AssetType(NetBoxObjectType):
    class Meta:
        model = Asset
        fields = "__all__"
        filterset_class = AssetFilterSet


class SupplierType(NetBoxObjectType):
    class Meta:
        model = Supplier
        fields = "__all__"
        filterset_class = SupplierFilterSet


class PurchaseType(NetBoxObjectType):
    class Meta:
        model = Purchase
        fields = "__all__"
        filterset_class = PurchaseFilterSet


class DeliveryType(NetBoxObjectType):
    class Meta:
        model = Delivery
        fields = "__all__"
        filterset_class = DeliveryFilterSet


class InventoryItemTypeType(NetBoxObjectType):
    class Meta:
        model = InventoryItemType
        fields = "__all__"
        filterset_class = InventoryItemTypeFilterSet


class InventoryItemGroupType(NetBoxObjectType):
    class Meta:
        model = InventoryItemGroup
        fields = "__all__"
        filterset_class = InventoryItemGroupFilterSet


class Query(ObjectType):
    asset = ObjectField(AssetType)
    supplier = ObjectField(SupplierType)
    purchase = ObjectField(PurchaseType)
    delivery = ObjectField(DeliveryType)
    inventory_item_type = ObjectField(InventoryItemTypeType)
    inventory_item_group = ObjectField(InventoryItemGroupType)

    asset_list = ObjectListField(AssetType)
    supplier_list = ObjectListField(SupplierType)
    purchase_list = ObjectListField(PurchaseType)
    delivery_list = ObjectListField(DeliveryType)
    inventory_item_type_list = ObjectListField(InventoryItemTypeType)
    inventory_item_group_list = ObjectListField(InventoryItemGroupType)


schema = Query
