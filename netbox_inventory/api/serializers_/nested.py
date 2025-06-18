from rest_framework import serializers

from netbox.api.serializers import WritableNestedSerializer

from netbox_inventory.models import InventoryItemGroup

__all__ = ('NestedInventoryItemGroupSerializer',)


class NestedInventoryItemGroupSerializer(WritableNestedSerializer):
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = InventoryItemGroup
        fields = ('id', 'url', 'display', 'name', 'description', '_depth')
