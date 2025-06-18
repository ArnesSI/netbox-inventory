from rest_framework import serializers

from netbox.api.serializers import WritableNestedSerializer

from netbox_inventory.models import Contract, InventoryItemGroup

__all__ = ('NestedContractSerializer', 'NestedInventoryItemGroupSerializer')


class NestedContractSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:contract-detail'
    )

    class Meta:
        model = Contract
        fields = ('id', 'url', 'display', 'name', 'contract_id')


class NestedInventoryItemGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:inventoryitemgroup-detail'
    )
    _depth = serializers.IntegerField(source='level', read_only=True)

    class Meta:
        model = InventoryItemGroup
        fields = ('id', 'url', 'display', 'name', 'description', '_depth')
