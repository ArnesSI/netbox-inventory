from dcim.api.serializers import LocationSerializer
from netbox.api.serializers import NetBoxModelSerializer
from rest_framework import serializers
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
    bom_ids = serializers.PrimaryKeyRelatedField(
        source='boms',
        queryset=BOM.objects.all(),
        many=True,
        required=False,
        write_only=True
    )
    boms = BOMSerializer(nested=True, many=True, read_only=True)
    asset_count = serializers.IntegerField(read_only=True)
    delivery_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Purchase
        fields = (
            'id',
            'url',
            'display',
            'supplier',
            'bom_ids',
            'boms',
            'name',
            'status',
            'date',
            'description',
            'comments',
            'tags',
            'custom_fields',
            'created',
            'last_updated',
            'asset_count',
            'delivery_count',
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
    purchase_ids = serializers.PrimaryKeyRelatedField(
        queryset=Purchase.objects.all(),
        source='purchases',
        many=True,
        required=False
    )
    purchases = PurchaseSerializer(nested=True, many=True, read_only=True)
    delivery_location = LocationSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None,
    )
    receiving_contact = ContactSerializer(
        nested=True, required=False, allow_null=True, default=None
    )
    asset_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Delivery
        fields = (
            'id',
            'url',
            'display',
            'delivery_location',
            'purchase_ids',
            'purchases',
            'name',
            'date',
            'description',
            'comments',
            'receiving_contact',
            'tags',
            'custom_fields',
            'created',
            'last_updated',
            'asset_count',
        )
        brief_fields = ('id', 'url', 'display', 'purchases', 'name', 'date', 'description')
