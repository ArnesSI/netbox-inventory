from django import forms

from dcim.models import Device, DeviceType, Manufacturer, ModuleType, Site, Location, Rack
from netbox.forms import NetBoxModelFilterSetForm
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES
from utilities.forms.fields import DynamicModelMultipleChoiceField, MultipleChoiceField, TagFilterField
from utilities.forms.widgets import DatePicker
from tenancy.forms import ContactModelFilterForm
from tenancy.models import Contact, Tenant
from ..choices import HardwareKindChoices, AssetStatusChoices
from ..models import Asset, InventoryItemType, InventoryItemGroup, Purchase, Supplier


__all__ = (
    'AssetFilterForm',
    'SupplierFilterForm',
    'PurchaseFilterForm',
    'InventoryItemTypeFilterForm',
    'InventoryItemGroupFilterForm',
)


class AssetFilterForm(NetBoxModelFilterSetForm):
    model = Asset
    fieldsets = (
        (None, ('q', 'filter_id', 'tag', 'status')),
        ('Hardware', (
            'kind', 'manufacturer_id', 'device_type_id', 'module_type_id',
            'inventoryitem_type_id', 'inventoryitem_group_id', 'is_assigned'
        )),
        ('Usage', ('tenant_id', 'contact_id')),
        ('Purchase', (
            'owner_id', 'purchase_id', 'supplier_id', 'purchase_date_after',
            'purchase_date_before', 'warranty_start_after', 'warranty_start_before',
            'warranty_end_after', 'warranty_end_before'
        )),
        ('Location', (
            'storage_site_id', 'storage_location_id', 'installed_site_id', 
            'installed_location_id', 'installed_rack_id', 'installed_device_id',
            'located_site_id', 'located_location_id',
        )),
    )

    status = MultipleChoiceField(
        choices=AssetStatusChoices,
        required=False,
    )
    kind = MultipleChoiceField(
        choices=HardwareKindChoices,
        required=False,
        help_text='Type of hardware',
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label='Manufacturer',
    )
    device_type_id = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer_id',
        },
        label='Device type',
    )
    module_type_id = DynamicModelMultipleChoiceField(
        queryset=ModuleType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer',
        },
        label='Module type',
    )
    inventoryitem_type_id = DynamicModelMultipleChoiceField(
        queryset=InventoryItemType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer',
        },
        label='Inventory item type'
    )
    inventoryitem_group_id = DynamicModelMultipleChoiceField(
        queryset=InventoryItemGroup.objects.all(),
        required=False,
        label='Inventory Item Group',
    )
    is_assigned = forms.NullBooleanField(
        required=False,
        label='Is assigned to hardware',
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        null_option='None',
        label='Tenant',
    )
    contact_id = DynamicModelMultipleChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        null_option='None',
        label='Contact',
    )
    owner_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        null_option='None',
        label='Owner',
    )
    purchase_id = DynamicModelMultipleChoiceField(
        queryset=Purchase.objects.all(),
        required=False,
        null_option='None',
        label='Purchase',
    )
    supplier_id = DynamicModelMultipleChoiceField(
        queryset=Supplier.objects.all(),
        required=False,
        label='Supplier',
    )
    purchase_date_after = forms.DateField(
        required=False,
        label='Purchased on or after',
        widget=DatePicker,
    )
    purchase_date_before = forms.DateField(
        required=False,
        label='Purchased on or before',
        widget=DatePicker,
    )
    warranty_start_after = forms.DateField(
        required=False,
        label='Warranty starts on or after',
        widget=DatePicker,
    )
    warranty_start_before = forms.DateField(
        required=False,
        label='Warranty starts on or before',
        widget=DatePicker,
    )
    warranty_end_after = forms.DateField(
        required=False,
        label='Warranty ends on or after',
        widget=DatePicker,
    )
    warranty_end_before = forms.DateField(
        required=False,
        label='Warranty ends on or before',
        widget=DatePicker,
    )
    storage_site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Storage site',
        help_text="When not in use asset is stored here",
    )
    storage_location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$storage_site_id',
        },
        label='Storage location',
        help_text="When not in use asset is stored here",
    )
    installed_site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Installed at site',
        help_text="Currently installed here",
    )
    installed_location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$installed_site_id',
        },
        label='Installed at location',
        help_text="Currently installed here",
    )
    installed_rack_id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$installed_site_id',
            'location_id': '$installed_location_id',
        },
        label='Installed in rack',
        help_text="Currently installed here",
    )
    installed_device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$installed_site_id',
            'location_id': '$installed_location_id',
            'rack_id': '$installed_rack_id',
        },
        label='Installed in device',
    )
    located_site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Located at site',
        help_text="Currently installed or stored here",
    )
    located_location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$located_site_id',
        },
        label='Located at location',
        help_text="Currently installed or stored here",
    )
    tag = TagFilterField(model)


class SupplierFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Supplier
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        ('Contacts', ('contact', 'contact_role', 'contact_group')),
    )

    tag = TagFilterField(model)


class PurchaseFilterForm(NetBoxModelFilterSetForm):
    model = Purchase
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        ('Purchase', ('supplier_id', 'date_after', 'date_before')),
    )

    supplier_id = DynamicModelMultipleChoiceField(
        queryset=Supplier.objects.all(),
        required=False,
        label='Supplier',
    )
    date_after = forms.DateField(
        required=False,
        label='Purchased on or after',
        widget=DatePicker,
    )
    date_before = forms.DateField(
        required=False,
        label='Purchased on or before',
        widget=DatePicker,
    )
    tag = TagFilterField(model)


class InventoryItemTypeFilterForm(NetBoxModelFilterSetForm):
    model = InventoryItemType
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        ('Inventory Item Type', ('manufacturer_id', 'inventoryitem_group_id')),
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label='Manufacturer',
    )
    inventoryitem_group_id = DynamicModelMultipleChoiceField(
        queryset=InventoryItemGroup.objects.all(),
        required=False,
        label='Inventory Item Group',
    )
    tag = TagFilterField(model)


class InventoryItemGroupFilterForm(NetBoxModelFilterSetForm):
    model = InventoryItemGroup
    fieldsets = (
        (None, ('q', 'filter_id', 'tag', 'parent_id')),
    )
    parent_id = DynamicModelMultipleChoiceField(
        queryset=InventoryItemGroup.objects.all(),
        required=False,
        label='Parent group'
    )
    tag = TagFilterField(model)
