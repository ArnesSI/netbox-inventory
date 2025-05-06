from dcim.models import (
    Device,
    DeviceRole,
    DeviceType,
    InventoryItemRole,
    Location,
    Manufacturer,
    ModuleType,
    Rack,
    RackRole,
    RackType,
    Site,
)
from django import forms
from netbox.forms import NetBoxModelFilterSetForm
from tenancy.forms import ContactModelFilterForm
from tenancy.models import Contact, ContactGroup, Tenant
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES
from utilities.forms.fields import (
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import DatePicker

from ..choices import (
    AssetStatusChoices,
    BOMStatusChoices,
    HardwareKindChoices,
    PurchaseStatusChoices,
    TransferStatusChoices,
)
from ..models import (
    BOM,
    Asset,
    Courier,
    Delivery,
    InventoryItemGroup,
    InventoryItemType,
    Purchase,
    Supplier,
    Transfer,
)

__all__ = (
    'AssetFilterForm',
    'SupplierFilterForm',
    'BOMFilterForm',
    'PurchaseFilterForm',
    'DeliveryFilterForm',
    'InventoryItemTypeFilterForm',
    'InventoryItemGroupFilterForm',
    'CourierFilterForm',
    'TransferFilterForm',
)


class AssetFilterForm(NetBoxModelFilterSetForm):
    model = Asset
    fieldsets = (
        FieldSet("q", "filter_id", "tag", "status"),
        FieldSet(
            "kind",
            "manufacturer_id",
            "device_type_id",
            "device_role_id",
            "module_type_id",
            "inventoryitem_type_id",
            "inventoryitem_group_id",
            "inventoryitem_role_id",
            "rack_type_id",
            "rack_role_id",
            "is_assigned",
            name="Hardware",
        ),
        FieldSet("tenant_id", "contact_group_id", "contact_id", name="Usage"),
        FieldSet(
            'owner_id',
            'bom_id',
            'delivery_id',
            'purchase_id',
            'supplier_id',
            'transfer_id',
            'delivery_date_after',
            'delivery_date_before',
            'purchase_date_after',
            'purchase_date_before',
            'warranty_start_after',
            'warranty_start_before',
            'warranty_end_after',
            'warranty_end_before',
            name='Purchase',
        ),
        FieldSet(
            "storage_site_id",
            "storage_location_id",
            "installed_site_id",
            "installed_location_id",
            "installed_rack_id",
            "installed_device_id",
            "located_site_id",
            "located_location_id",
            name="Location",
        ),
    )

    status = forms.MultipleChoiceField(
        choices=AssetStatusChoices,
        required=False,
    )
    kind = forms.MultipleChoiceField(
        choices=HardwareKindChoices,
        required=False,
        help_text="Type of hardware",
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label="Manufacturer",
    )
    device_type_id = DynamicModelMultipleChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        query_params={
            "manufacturer_id": "$manufacturer_id",
        },
        label="Device type",
    )
    device_role_id = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        label="Device role",
    )
    module_type_id = DynamicModelMultipleChoiceField(
        queryset=ModuleType.objects.all(),
        required=False,
        query_params={
            "manufacturer_id": "$manufacturer",
        },
        label="Module type",
    )
    inventoryitem_type_id = DynamicModelMultipleChoiceField(
        queryset=InventoryItemType.objects.all(),
        required=False,
        query_params={
            "manufacturer_id": "$manufacturer",
        },
        label="Inventory item type",
    )
    inventoryitem_group_id = DynamicModelMultipleChoiceField(
        queryset=InventoryItemGroup.objects.all(),
        required=False,
        label="Inventory item group",
    )
    inventoryitem_role_id = DynamicModelMultipleChoiceField(
        queryset=InventoryItemRole.objects.all(),
        required=False,
        label="Inventory item role",
    )
    rack_type_id = DynamicModelMultipleChoiceField(
        queryset=RackType.objects.all(),
        required=False,
        query_params={
            "manufacturer_id": "$manufacturer_id",
        },
        label="Rack type",
    )
    rack_role_id = DynamicModelMultipleChoiceField(
        queryset=RackRole.objects.all(),
        required=False,
        label="Rack role",
    )
    is_assigned = forms.NullBooleanField(
        required=False,
        label="Is assigned to hardware",
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES),
    )
    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        null_option="None",
        label="Tenant",
    )
    contact_group_id = DynamicModelMultipleChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        null_option="None",
        label="Contact Group",
    )
    contact_id = DynamicModelMultipleChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        null_option="None",
        query_params={
            "group_id": "$contact_group_id",
        },
        label="Contact",
    )
    owner_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        null_option="None",
        label="Owner",
    )
    bom_id = DynamicModelMultipleChoiceField(
        queryset=BOM.objects.all(),
        required=False,
        null_option="None",
        label="BOM",
    )
    delivery_id = DynamicModelMultipleChoiceField(
        queryset=Delivery.objects.all(),
        required=False,
        null_option="None",
        label="Delivery",
    )
    purchase_id = DynamicModelMultipleChoiceField(
        queryset=Purchase.objects.all(),
        required=False,
        null_option="None",
        label="Purchase",
    )
    supplier_id = DynamicModelMultipleChoiceField(
        queryset=Supplier.objects.all(),
        required=False,
        label="Supplier",
    )
    transfer_id = DynamicModelMultipleChoiceField(
        queryset=Transfer.objects.all(),
        required=False,
        label='Transfer',
    )
    delivery_date_after = forms.DateField(
        required=False,
        label="Delivered on or after",
        widget=DatePicker,
    )
    delivery_date_before = forms.DateField(
        required=False,
        label="Delivered on or before",
        widget=DatePicker,
    )
    purchase_date_after = forms.DateField(
        required=False,
        label="Purchased on or after",
        widget=DatePicker,
    )
    purchase_date_before = forms.DateField(
        required=False,
        label="Purchased on or before",
        widget=DatePicker,
    )
    warranty_start_after = forms.DateField(
        required=False,
        label="Warranty starts on or after",
        widget=DatePicker,
    )
    warranty_start_before = forms.DateField(
        required=False,
        label="Warranty starts on or before",
        widget=DatePicker,
    )
    warranty_end_after = forms.DateField(
        required=False,
        label="Warranty ends on or after",
        widget=DatePicker,
    )
    warranty_end_before = forms.DateField(
        required=False,
        label="Warranty ends on or before",
        widget=DatePicker,
    )
    storage_site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label="Storage site",
        help_text="When not in use asset is stored here",
    )
    storage_location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        null_option="None",
        query_params={
            "site_id": "$storage_site_id",
        },
        label="Storage location",
        help_text="When not in use asset is stored here",
    )
    installed_site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label="Installed at site",
        help_text="Currently installed here",
    )
    installed_location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            "site_id": "$installed_site_id",
        },
        label="Installed at location",
        help_text="Currently installed here",
    )
    installed_rack_id = DynamicModelMultipleChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        query_params={
            "site_id": "$installed_site_id",
            "location_id": "$installed_location_id",
        },
        label="Installed in rack",
        help_text="Currently installed here",
    )
    installed_device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        query_params={
            "site_id": "$installed_site_id",
            "location_id": "$installed_location_id",
            "rack_id": "$installed_rack_id",
        },
        label="Installed in device",
    )
    located_site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label="Located at site",
        help_text="Currently installed or stored here",
    )
    located_location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            "site_id": "$located_site_id",
        },
        label="Located at location",
        help_text="Currently installed or stored here",
    )
    tag = TagFilterField(model)


class SupplierFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Supplier
    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet("contact_group", "contact_role", "contact", name="Contacts"),
    )

    contact_group = DynamicModelMultipleChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        null_option="None",
        label="Contact Group",
    )
    contact = DynamicModelMultipleChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        null_option="None",
        query_params={
            "group_id": "$contact_group",
        },
        label="Contact",
    )

    tag = TagFilterField(model)


class BOMFilterForm(NetBoxModelFilterSetForm):
    model = BOM
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('status', 'purchase_id', name='BOM'),
    )

    status = forms.MultipleChoiceField(
        choices=BOMStatusChoices,
        required=False,
    )
    purchase_id = DynamicModelChoiceField(
        queryset=Purchase.objects.all(),
        required=False,
        label='Purchase',
    )
    tag = TagFilterField(model)


class PurchaseFilterForm(NetBoxModelFilterSetForm):
    model = Purchase
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet(
            'supplier_id',
            'boms',
            'status',
            'delivery_id',
            'date_after',
            'date_before',
            name='Purchase',
        ),
    )

    supplier_id = DynamicModelMultipleChoiceField(
        queryset=Supplier.objects.all(),
        required=False,
        label="Supplier",
    )
    boms = DynamicModelMultipleChoiceField(
        queryset=BOM.objects.all(),
        required=False,
        label="BOMs",
    )
    status = forms.MultipleChoiceField(
        choices=PurchaseStatusChoices,
        required=False,
    )
    delivery_id = DynamicModelChoiceField(
        queryset=Delivery.objects.all(),
        required=False,
        label='Delivery',
    )
    date_after = forms.DateField(
        required=False,
        label="Purchased on or after",
        widget=DatePicker,
    )
    date_before = forms.DateField(
        required=False,
        label="Purchased on or before",
        widget=DatePicker,
    )
    tag = TagFilterField(model)


class DeliveryFilterForm(NetBoxModelFilterSetForm):
    model = Delivery
    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet(
            'purchase_id',
            'supplier_id',
            'delivery_site_id',
            'delivery_location_id',
            'contact_group_id',
            'receiving_contact_id',
            'date_after',
            'date_before',
            name='Delivery',
        ),
    )

    purchase_id = DynamicModelMultipleChoiceField(
        queryset=Purchase.objects.all(),
        required=False,
        label="Purchase",
    )
    supplier_id = DynamicModelMultipleChoiceField(
        queryset=Supplier.objects.all(),
        required=False,
        label="Supplier",
    )
    contact_group_id = DynamicModelMultipleChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        null_option="None",
        label="Contact Group",
    )
    delivery_site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Delivery site',
        help_text='Site where this delivery was received',
    )
    delivery_location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$delivery_site_id',
        },
        label='Delivery location',
        help_text='Location where this delivery was received',
    )
    receiving_contact_id = DynamicModelMultipleChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        query_params={
            "group_id": "$contact_group_id",
        },
        label="Receiving contact",
    )
    date_after = forms.DateField(
        required=False,
        label="Delivered on or after",
        widget=DatePicker,
    )
    date_before = forms.DateField(
        required=False,
        label="Delivered on or before",
        widget=DatePicker,
    )
    tag = TagFilterField(model)


class InventoryItemTypeFilterForm(NetBoxModelFilterSetForm):
    model = InventoryItemType
    fieldsets = (
        FieldSet("q", "filter_id", "tag"),
        FieldSet(
            "manufacturer_id", "inventoryitem_group_id", name="Inventory Item Type"
        ),
    )
    manufacturer_id = DynamicModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label="Manufacturer",
    )
    inventoryitem_group_id = DynamicModelMultipleChoiceField(
        queryset=InventoryItemGroup.objects.all(),
        required=False,
        label="Inventory Item Group",
    )
    tag = TagFilterField(model)


class InventoryItemGroupFilterForm(NetBoxModelFilterSetForm):
    model = InventoryItemGroup
    fieldsets = (FieldSet("q", "filter_id", "tag", "parent_id"),)
    parent_id = DynamicModelMultipleChoiceField(
        queryset=InventoryItemGroup.objects.all(), required=False, label="Parent group"
    )
    tag = TagFilterField(model)


class CourierFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Courier
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('contact_group', 'contact_role', 'contact', name='Contacts'),
    )

    contact_group = DynamicModelMultipleChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        null_option='None',
        label='Contact Group',
    )
    contact = DynamicModelMultipleChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'group_id': '$contact_group',
        },
        label='Contact',
    )

    tag = TagFilterField(model)


class TransferFilterForm(NetBoxModelFilterSetForm):
    model = Transfer
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag', 'status'),
        FieldSet('asset_id', 'courier_id', name='General'),
        FieldSet(
            'sender_group_id',
            'sender_id',
            'recipient_group_id',
            'recipient_id',
            name='Contacts',
        ),
        FieldSet(
            'site_id',
            'location_id',
            'pickup_date_after',
            'pickup_date_before',
            'received_date_after',
            'received_date_before',
            name='Transfer',
        ),
    )

    asset_id = DynamicModelMultipleChoiceField(
        queryset=Asset.objects.all(),
        required=False,
        label='Assets',
    )
    courier_id = DynamicModelMultipleChoiceField(
        queryset=Courier.objects.all(),
        required=False,
        label='Courier',
    )
    status = forms.MultipleChoiceField(
        choices=TransferStatusChoices,
        required=False,
    )
    sender_group_id = DynamicModelMultipleChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        null_option='None',
        label='Sender Group',
    )
    sender_id = DynamicModelMultipleChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'group_id': '$sender_group_id',
        },
        label='Sender',
    )
    recipient_group_id = DynamicModelMultipleChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        null_option='None',
        label='Recipient Group',
    )
    recipient_id = DynamicModelMultipleChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'group_id': '$recipient_group_id',
        },
        label='Recipient',
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Delivered at site',
        help_text='Transfer delivered here',
    )
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site_id',
        },
        label='Delivered at location on site',
        help_text='Transfer delivered here',
    )
    pickup_date_after = forms.DateField(
        required=False,
        label='Transfer picked up on or after',
        widget=DatePicker,
    )
    pickup_date_before = forms.DateField(
        required=False,
        label='Transfer picked up on or before',
        widget=DatePicker,
    )
    received_date_after = forms.DateField(
        required=False,
        label='Transfer received on or after',
        widget=DatePicker,
    )
    received_date_before = forms.DateField(
        required=False,
        label='Transfer received on or before',
        widget=DatePicker,
    )
    tag = TagFilterField(model)
