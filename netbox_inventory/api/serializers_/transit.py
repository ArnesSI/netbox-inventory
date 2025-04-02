from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer

from netbox_inventory.models import Courier

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