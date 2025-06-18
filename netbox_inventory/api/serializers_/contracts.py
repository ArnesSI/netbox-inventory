from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers import ContactSerializer

from .deliveries import SupplierSerializer
from netbox_inventory.models import Contract


class ContractSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_inventory-api:contract-detail'
    )
    supplier = SupplierSerializer(nested=True)
    contact = ContactSerializer(
        nested=True, required=False, allow_null=True, default=None
    )
    asset_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Contract
        fields = (
            'id',
            'url',
            'display',
            'name',
            'contract_id',
            'supplier',
            'contract_type',
            'status',
            'start_date',
            'end_date',
            'renewal_date',
            'cost',
            'currency',
            'contact',
            'description',
            'comments',
            'tags',
            'custom_fields',
            'created',
            'last_updated',
            'asset_count',
        )
        brief_fields = (
            'id',
            'url',
            'display',
            'name',
            'contract_id',
            'supplier',
            'contract_type',
            'status',
            'start_date',
            'end_date',
        ) 