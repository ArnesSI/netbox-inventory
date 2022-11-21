from cProfile import label
from django import forms

from dcim.models import DeviceType, Manufacturer, ModuleType, Site, Location
from netbox.forms import NetBoxModelFilterSetForm
from utilities.forms import (
    DatePicker, DynamicModelMultipleChoiceField, MultipleChoiceField,
    StaticSelect, TagFilterField, BOOLEAN_WITH_BLANK_CHOICES
)
from tenancy.models import Contact, Tenant
from ..choices import HardwareKindChoices, InventoryStatusChoices
from ..models import Asset, InventoryItemType, Purchase, Supplier


__all__ = (
    'AssetFilterForm',
    'SupplierFilterForm',
    'PurchaseFilterForm',
)


class AssetFilterForm(NetBoxModelFilterSetForm):
    model = Asset
    fieldsets = (
        (None, ('q', 'tag', 'status')),
        ('Hardware', (
            'kind', 'manufacturer_id', 'device_type_id', 'module_type_id',
            'inventoryitem_type_id', 'is_assigned'
        )),
        ('Usage', ('tenant_id', 'contact_id')),
        ('Purchase', (
            'owner_id', 'purchase_id', 'supplier_id', 'purchase_date_after',
            'purchase_date_before', 'warranty_start_after', 'warranty_start_before',
            'warranty_end_after', 'warranty_end_before'
        )),
        ('Location', ('storage_site_id', 'storage_location_id')),
    )

    status = MultipleChoiceField(
        choices=InventoryStatusChoices,
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
    is_assigned = forms.NullBooleanField(
        required=False,
        label='Is assigned to hardware',
        widget=StaticSelect(
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
    )
    storage_location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$storage_site_id',
        },
        label='Storage location',

    )
    tag = TagFilterField(model)


class SupplierFilterForm(NetBoxModelFilterSetForm):
    model = Supplier
    tag = TagFilterField(model)


class PurchaseFilterForm(NetBoxModelFilterSetForm):
    model = Purchase

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
