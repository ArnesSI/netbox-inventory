from django.db.models import Q
import django_filters

from dcim.filtersets import DeviceFilterSet
from dcim.models import Manufacturer
from netbox.filtersets import NetBoxModelFilterSet
from utilities import filters
from .models import Asset, InventoryItemType, Purchase, Supplier


class AssetFilterSet(NetBoxModelFilterSet):
    manufacturer = filters.MultiValueCharFilter(method='filter_manufacturer')
    inventoryitem_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name='inventoryitem_type',
        queryset=InventoryItemType.objects.all(),
        label='Inventory item type (ID)',
    )
    inventoryitem_type = django_filters.ModelMultipleChoiceFilter(
        field_name='inventoryitem_type__slug',
        queryset=InventoryItemType.objects.all(),
        label='Inventory item type (slug)',
    )
    supplier_id = django_filters.ModelMultipleChoiceFilter(
        field_name='purchase__supplier',
        queryset=Supplier.objects.all(),
        label='Supplier (ID)',
    )
    supplier = django_filters.ModelMultipleChoiceFilter(
        field_name='purchase__supplier__name',
        queryset=Supplier.objects.all(),
        label='Supplier (name)',
    )

    class Meta:
        model = Asset
        fields = (
            'id', 'serial', 'status', 'manufacturer', 'device_type', 'module_type',
            'inventoryitem_type_id', 'inventoryitem_type', 'supplier_id', 'supplier',
        )

    def search(self, queryset, name, value):
        query = Q(
            Q(serial__icontains=value)|
            Q(name__icontains=value)|
            Q(asset_tag__iexact=value)|
            Q(device_type__model__icontains=value)|
            Q(module_type__model__icontains=value)|
            Q(inventoryitem_type__model__icontains=value)
        )
        return queryset.filter(query)

    def filter_manufacturer(self, queryset, name, value):
        return queryset.filter(
            Q(device_type__manufacturer__in=value)|
            Q(module_type__manufacturer__in=value)|
            Q(inventoryitem_type__manufacturer__in=value)
        )


class DeviceAssetFilterSet(DeviceFilterSet):
    has_asset_assigned = django_filters.BooleanFilter(
        method='_has_asset_assigned',
        label='Has an asset assigned',
    )

    def _has_asset_assigned(self, queryset, name, value):
        params = Q(assigned_asset__isnull=False)
        if value:
            return queryset.filter(params)
        return queryset.exclude(params)


class SupplierFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = Supplier
        fields = (
            'id', 'name', 'slug', 'description',
        )

    def search(self, queryset, name, value):
        query = Q(
            Q(name__icontains=value) |
            Q(slug__icontains=value) |
            Q(description__icontains=value)
        )
        return queryset.filter(query)


class PurchaseFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = Purchase
        fields = (
            'id', 'supplier', 'name', 'description'
        )

    def search(self, queryset, name, value):
        query = Q(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(supplier__name__icontains=value)
        )
        return queryset.filter(query)


class InventoryItemTypeFilterSet(NetBoxModelFilterSet):
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        field_name='manufacturer',
        queryset=Manufacturer.objects.all(),
        label='Manufacturer (ID)',
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name='manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        label='Manufacturer (slug)',
    )

    class Meta:
        model = InventoryItemType
        fields = (
            'id', 'manufacturer_id', 'manufacturer', 'model', 'slug', 'part_number'
        )

    def search(self, queryset, name, value):
        query = Q(
            Q(model__icontains=value) |
            Q(part_number__icontains=value)
        )
        return queryset.filter(query)
