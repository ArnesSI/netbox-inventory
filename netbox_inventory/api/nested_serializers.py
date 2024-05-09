from rest_framework import serializers

from netbox.api.serializers import WritableNestedSerializer
from ..models import InventoryItemGroup

__all__ = (
    'NestedInventoryItemGroupSerializer',
)


class NestedInventoryItemGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:inventoryitemgroup-detail'
    )
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = InventoryItemGroup
        fields = ('id', 'url', 'display', 'name', '_depth')
