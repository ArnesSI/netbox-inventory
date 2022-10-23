from django.db.models import Q
import django_filters

from dcim.filtersets import DeviceFilterSet, InventoryItemFilterSet, ModuleFilterSet
from dcim.models import Manufacturer, DeviceType, ModuleType, Site, Location
from netbox.filtersets import NetBoxModelFilterSet
from utilities import filters
from tenancy.models import Contact, Tenant
from .choices import HardwareKindChoices, InventoryStatusChoices
from .models import Asset, InventoryItemType, Purchase, Supplier


class AssetFilterSet(NetBoxModelFilterSet):
    status = django_filters.MultipleChoiceFilter(
        choices=InventoryStatusChoices,
    )
    kind = filters.MultiValueCharFilter(
        method='filter_kind',
        label='Type of hardware',
    )
    manufacturer_id = filters.MultiValueCharFilter(
        method='filter_manufacturer',
        label='Manufacturer (ID)',
    )
    device_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device_type',
        queryset=DeviceType.objects.all(),
        label='Device type (ID)',
    )
    device_type = django_filters.ModelMultipleChoiceFilter(
        field_name='device_type__slug',
        queryset=DeviceType.objects.all(),
        to_field_name='slug',
        label='Device type (slug)',
    )
    module_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name='module_type',
        queryset=ModuleType.objects.all(),
        label='Module type (ID)',
    )
    inventoryitem_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name='inventoryitem_type',
        queryset=InventoryItemType.objects.all(),
        label='Inventory item type (ID)',
    )
    inventoryitem_type = django_filters.ModelMultipleChoiceFilter(
        field_name='inventoryitem_type__slug',
        queryset=InventoryItemType.objects.all(),
        to_field_name='slug',
        label='Inventory item type (slug)',
    )
    is_assigned = django_filters.BooleanFilter(
        method='filter_is_assigned',
        label='Is assigned to hardware',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        field_name='tenant',
        label='Tenant (ID)',
    )
    contact_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Contact.objects.all(),
        field_name='contact',
        label='Contact (ID)',
    )
    owner_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        field_name='owner',
        label='Owner (ID)',
    )
    purchase_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Purchase.objects.all(),
        field_name='purchase',
        label='Purchase (ID)',
    )
    purchase = django_filters.CharFilter(
        field_name='purchase__name',
        lookup_expr='iexact',
        label='Purchase (name)',
    )
    supplier_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Supplier.objects.all(),
        field_name='purchase__supplier',
        label='Supplier (ID)',
    )
    supplier = django_filters.CharFilter(
        field_name='purchase__supplier__name',
        lookup_expr='iexact',
        label='Supplier (name)',
    )
    warranty_start = django_filters.DateFromToRangeFilter()
    warranty_end = django_filters.DateFromToRangeFilter()
    purchase_date = django_filters.DateFromToRangeFilter(
        field_name='purchase__date',
    )
    storage_site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        field_name='storage_location__site',
        label='Storage site (ID)',
    )
    storage_location_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='storage_location',
        label='Storage location (ID)',
    )

    class Meta:
        model = Asset
        fields = ('id', 'name', 'serial', 'asset_tag')

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

    def filter_kind(self, queryset, name, value):
        query = None
        for kind in HardwareKindChoices.values():
            if kind in value:
                q = Q(**{f'{kind}_type__isnull':False})
                if query:
                    query = query|q
                else:
                    query = q
        if query:
            return queryset.filter(query)
        else:
            return queryset

    def filter_manufacturer(self, queryset, name, value):
        return queryset.filter(
            Q(device_type__manufacturer__in=value)|
            Q(module_type__manufacturer__in=value)|
            Q(inventoryitem_type__manufacturer__in=value)
        )

    def filter_is_assigned(self, queryset, name, value):
        if value:
            # is assigned to any hardware
            return queryset.filter(
                Q(device__isnull=False)|
                Q(module__isnull=False)|
                Q(inventoryitem__isnull=False)
            )
        else:
            # is not assigned to hardware kind
            return queryset.filter(
                Q(device__isnull=True)&
                Q(module__isnull=True)&
                Q(inventoryitem__isnull=True)
            )


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
    supplier_id = django_filters.ModelMultipleChoiceFilter(
        field_name='supplier',
        queryset=Supplier.objects.all(),
        label='Supplier (ID)',
    )
    date = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Purchase
        fields = (
            'id', 'supplier', 'name', 'date', 'description'
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


class HasAssetFilterMixin(NetBoxModelFilterSet):
    has_asset_assigned = django_filters.BooleanFilter(
        method='_has_asset_assigned',
        label='Has an asset assigned',
    )

    def _has_asset_assigned(self, queryset, name, value):
        params = Q(assigned_asset__isnull=False)
        if value:
            return queryset.filter(params)
        return queryset.exclude(params)


class DeviceAssetFilterSet(HasAssetFilterMixin, DeviceFilterSet):
    pass

class ModuleAssetFilterSet(HasAssetFilterMixin, ModuleFilterSet):
    pass

class InventoryItemAssetFilterSet(HasAssetFilterMixin, InventoryItemFilterSet):
    pass
