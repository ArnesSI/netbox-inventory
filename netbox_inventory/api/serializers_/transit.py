from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer

from netbox_inventory.models import Courier, Transfer

from .nested import *


class CourierSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:courier-detail'
    )
    # TODO: Transfer model
    # transfer_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Courier
        fields = (
            'id',
            'url',
            'display',
            'name',
            'slug',
            'description',
            'comments',
            'tags',
            'custom_fields',
            'created',
            'last_updated',
            # TODO: Transfer model
            # 'transfer_count',
        )
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description')


class TransferSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:transfer-detail'
    )
    # TODO: Asset model
    # asset_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Transfer
        fields = (
            'id',
            'url',
            'display',
            'name',
            'courier',
            'shipping_number',
            'instructions',
            'status',
            'sender',
            'recipient',
            'site',
            'location',
            'pickup_date',
            'received_date',
            'comments',
            'tags',
            'custom_fields',
            'created',
            'last_updated',
        )
        brief_fields = ('id', 'url', 'display', 'name', 'courier', 'status')