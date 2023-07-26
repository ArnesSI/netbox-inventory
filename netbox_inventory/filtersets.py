from django.db.models import Q
import django_filters

from dcim.filtersets import DeviceFilterSet, InventoryItemFilterSet, ModuleFilterSet
from dcim.models import Manufacturer, DeviceType, ModuleType, Site, Location
from netbox.filtersets import NetBoxModelFilterSet
from utilities import filters
from tenancy.filtersets import ContactModelFilterSet
from tenancy.models import Contact, Tenant
from .choices import HardwareKindChoices, AssetStatusChoices
from .models import Asset, Delivery, InventoryItemType, InventoryItemGroup, Purchase, Supplier
from .utils import query_located, get_asset_custom_fields_search_filters


class AssetFilterSet(NetBoxModelFilterSet):
    status = django_filters.MultipleChoiceFilter(
        choices=AssetStatusChoices,
    )
    kind = filters.MultiValueCharFilter(
        method='filter_kind',
        label='Type of hardware',
    )
    manufacturer_id = filters.MultiValueCharFilter(
        method='filter_manufacturer',
        label='Manufacturer (ID)',
    )
    manufacturer_name = filters.MultiValueCharFilter(
        method='filter_manufacturer',
        label='Manufacturer (name)',
    )
    device_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device_type',
        queryset=DeviceType.objects.all(),
        label='Device type (ID)',
    )
    device_type = filters.MultiValueCharFilter(
        field_name='device_type__slug',
        lookup_expr='iexact',
        label='Device type (slug)',
    )
    device_type_model = filters.MultiValueCharFilter(
        field_name='device_type__model',
        lookup_expr='icontains',
        label='Device type (model)',
    )
    module_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name='module_type',
        queryset=ModuleType.objects.all(),
        label='Module type (ID)',
    )
    module_type_model = filters.MultiValueCharFilter(
        field_name='module_type__model',
        lookup_expr='icontains',
        label='Module_type (model)',
    )
    inventoryitem_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name='inventoryitem_type',
        queryset=InventoryItemType.objects.all(),
        label='Inventory item type (ID)',
    )
    inventoryitem_type = filters.MultiValueCharFilter(
        field_name='inventoryitem_type__slug',
        lookup_expr='iexact',
        label='Inventory item type (slug)',
    )
    inventoryitem_type_model = filters.MultiValueCharFilter(
        field_name='inventoryitem_type__model',
        lookup_expr='icontains',
        label='Inventory item type (model)',
    )
    inventoryitem_group_id = filters.TreeNodeMultipleChoiceFilter(
        field_name='inventoryitem_type__inventoryitem_group',
        queryset=InventoryItemGroup.objects.all(),
        lookup_expr='in',
        label='Inventory item group (ID)',
    )
    inventoryitem_group_name = filters.MultiValueCharFilter(
        field_name='inventoryitem_type__inventoryitem_group__name',
        lookup_expr='icontains',
        label='Inventory item group (name)',
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
    tenant = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        field_name='tenant__slug',
        to_field_name='slug',
        label='Tenant (slug)',
    )
    tenant_name = filters.MultiValueCharFilter(
        field_name='tenant__name',
        lookup_expr='icontains',
        label='Tenant (name)',
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
    owner = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        field_name='owner__slug',
        to_field_name='slug',
        label='Owner (slug)',
    )
    owner_name = filters.MultiValueCharFilter(
        field_name='owner__name',
        lookup_expr='icontains',
        label='Owner (name)',
    )
    delivery_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Delivery.objects.all(),
        field_name='delivery',
        label='Delivery (ID)',
    )
    delivery = django_filters.CharFilter(
        field_name='delivery__name',
        lookup_expr='iexact',
        label='Delivery (name)',
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
    delivery_date = django_filters.DateFromToRangeFilter(
        field_name='delivery__date',
    )
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
    installed_site_slug = filters.MultiValueCharFilter(
        method='filter_installed_site_slug',
        label='Installed site (slug)',
    )
    installed_site_id = filters.MultiValueCharFilter(
        method='filter_installed',
        field_name='site',
        label='Installed site (ID)',
    )
    installed_location_id = filters.MultiValueCharFilter(
        method='filter_installed',
        field_name='location',
        label='Installed location (ID)',
    )
    installed_rack_id = filters.MultiValueCharFilter(
        method='filter_installed',
        field_name='rack',
        label='Installed rack (ID)',
    )
    installed_device_id = filters.MultiValueCharFilter(
        method='filter_installed_device',
        field_name='id',
        label='Installed device (ID)',
    )
    installed_device_name = filters.MultiValueCharFilter(
        method='filter_installed_device',
        field_name='name',
        label='Installed device (name)',
    )
    located_site_id = filters.MultiValueCharFilter(
        method='filter_located',
        field_name='site',
        label='Located site (ID)',
    )
    located_location_id = filters.MultiValueCharFilter(
        method='filter_located',
        field_name='location',
        label='Located location (ID)',
    )

    class Meta:
        model = Asset
        fields = ('id', 'name', 'serial', 'asset_tag')

    def search(self, queryset, name, value):
        query = (
            Q(serial__icontains=value)
            | Q(name__icontains=value)
            | Q(asset_tag__icontains=value)
            | Q(device_type__model__icontains=value)
            | Q(module_type__model__icontains=value)
            | Q(inventoryitem_type__model__icontains=value)
            | Q(delivery__name__icontains=value)
            | Q(purchase__name__icontains=value)
            | Q(purchase__supplier__name__icontains=value)
        )
        custom_field_filters = get_asset_custom_fields_search_filters()
        for custom_field_filter in custom_field_filters:
            query |= Q(**{custom_field_filter: value})

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
        if name == 'manufacturer_id':
            return queryset.filter(
                Q(device_type__manufacturer__in=value)|
                Q(module_type__manufacturer__in=value)|
                Q(inventoryitem_type__manufacturer__in=value)
            )
        elif name == 'manufacturer_name':
            # OR for every passed value and for all hardware types
            q = Q()
            for v in value:
                q |= Q(device_type__manufacturer__name__icontains=v)
                q |= Q(module_type__manufacturer__name__icontains=v)
                q |= Q(inventoryitem_type__manufacturer__name__icontains=v)
            return queryset.filter(q)

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

    def filter_installed(self, queryset, name, value):
        return query_located(queryset, name, value, assets_shown='installed')

    def filter_installed_site_slug(self, queryset, name, value):
        return query_located(queryset, 'site__slug', value, assets_shown='installed')

    def filter_installed_device(self, queryset, name, value):
        return query_located(queryset, name, value, assets_shown='installed')

    def filter_located(self, queryset, name, value):
        return query_located(queryset, name, value)


class SupplierFilterSet(NetBoxModelFilterSet, ContactModelFilterSet):
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


class DeliveryFilterSet(NetBoxModelFilterSet):
    purchase_id = django_filters.ModelMultipleChoiceFilter(
        field_name='purchase',
        queryset=Purchase.objects.all(),
        label='Purchase (ID)',
    )
    supplier_id = django_filters.ModelMultipleChoiceFilter(
        field_name='purchase__supplier',
        queryset=Supplier.objects.all(),
        label='Supplier (ID)',
    )
    receiving_contact_id = django_filters.ModelMultipleChoiceFilter(
        field_name='receiving_contact',
        queryset=Contact.objects.all(),
        label='Contact (ID)',
    )
    date = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Delivery
        fields = (
            'id', 'name', 'date', 'description', 'receiving_contact', 'purchase',
        )

    def search(self, queryset, name, value):
        query = Q(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(purchase__name__icontains=value) |
            Q(purchase__supplier__name__icontains=value) |
            Q(receiving_contact__name__icontains=value)
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
    inventoryitem_group_id = filters.TreeNodeMultipleChoiceFilter(
        field_name='inventoryitem_group',
        queryset=InventoryItemGroup.objects.all(),
        lookup_expr='in',
        label='Inventory item group (ID)',
    )

    class Meta:
        model = InventoryItemType
        fields = (
            'id', 'manufacturer_id', 'manufacturer', 'model', 'slug', 'part_number',
            'inventoryitem_group_id',
        )

    def search(self, queryset, name, value):
        query = Q(
            Q(model__icontains=value) |
            Q(part_number__icontains=value)
        )
        return queryset.filter(query)


class InventoryItemGroupFilterSet(NetBoxModelFilterSet):
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=InventoryItemGroup.objects.all(),
        label='Parent group (ID)',
    )

    class Meta:
        model = InventoryItemGroup
        fields = (
            'id', 'name'
        )

    def search(self, queryset, name, value):
        query = Q(name__icontains=value) 
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
