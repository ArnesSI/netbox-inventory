from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers import ContactSerializer

from netbox_inventory.models import BOM, Delivery, Purchase, Supplier

from .nested import *


class SupplierSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_inventory-api:supplier-detail"
    )
    asset_count = serializers.IntegerField(read_only=True)
    purchase_count = serializers.IntegerField(read_only=True)
    delivery_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Supplier
        fields = (
            "id",
            "url",
            "display",
            "name",
            "slug",
            "description",
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
            "asset_count",
            "purchase_count",
            "delivery_count",
        )
        brief_fields = ("id", "url", "display", "name", "slug", "description")


class BOMSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_inventory-api:bom-detail"
    )
    asset_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = BOM
        fields = (
            "id",
            "url",
            "display",
            "name",
            "status",
            "description",
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
            "asset_count",
        )
        brief_fields = ("id", "url", "display", "name", "status", "description")


class PurchaseSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_inventory-api:purchase-detail"
    )
    supplier = SupplierSerializer(nested=True)
    boms = BOMSerializer(nested=True, many=True)
    asset_count = serializers.IntegerField(read_only=True)
    delivery_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Purchase
        fields = (
            "id",
            "url",
            "display",
            "supplier",
            "boms",
            "name",
            "status",
            "date",
            "description",
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
            "asset_count",
            "delivery_count",
        )
        brief_fields = (
            "id",
            "url",
            "display",
            "supplier",
            "boms",
            "name",
            "status",
            "date",
            "description",
        )


class DeliverySerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_inventory-api:delivery-detail"
    )
    purchase = PurchaseSerializer(nested=True)
    receiving_contact = ContactSerializer(
        nested=True, required=False, allow_null=True, default=None
    )
    asset_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Delivery
        fields = (
            "id",
            "url",
            "display",
            "purchase",
            "name",
            "date",
            "description",
            "comments",
            "receiving_contact",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
            "asset_count",
        )
        brief_fields = ("id", "url", "display", "name", "date", "description")
