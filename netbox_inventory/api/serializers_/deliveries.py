from rest_framework import serializers

from netbox.api.serializers import PrimaryModelSerializer
from tenancy.api.serializers import ContactSerializer

from .nested import *
from netbox_inventory.models import Delivery, Purchase, Supplier


class SupplierSerializer(PrimaryModelSerializer):
    asset_count = serializers.IntegerField(read_only=True)
    purchase_count = serializers.IntegerField(read_only=True)
    delivery_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Supplier
        fields = (
            'id',
            'url',
            'display',
            'name',
            'slug',
            'description',
            'owner',
            'comments',
            'tags',
            'custom_fields',
            'created',
            'last_updated',
            'asset_count',
            'purchase_count',
            'delivery_count',
        )
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description')


class PurchaseSerializer(PrimaryModelSerializer):
    supplier = SupplierSerializer(nested=True)
    asset_count = serializers.IntegerField(read_only=True)
    delivery_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Purchase
        fields = (
            'id',
            'url',
            'display',
            'supplier',
            'name',
            'status',
            'date',
            'description',
            'owner',
            'comments',
            'tags',
            'custom_fields',
            'created',
            'last_updated',
            'asset_count',
            'delivery_count',
        )
        brief_fields = (
            'id',
            'url',
            'display',
            'supplier',
            'name',
            'status',
            'date',
            'description',
        )


class DeliverySerializer(PrimaryModelSerializer):
    purchase = PurchaseSerializer(nested=True)
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
            'purchase',
            'name',
            'date',
            'description',
            'owner',
            'comments',
            'receiving_contact',
            'tags',
            'custom_fields',
            'created',
            'last_updated',
            'asset_count',
        )
        brief_fields = ('id', 'url', 'display', 'name', 'date', 'description')
