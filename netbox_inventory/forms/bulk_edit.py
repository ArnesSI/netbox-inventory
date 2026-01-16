from django import forms
from django.utils.translation import gettext_lazy as _

from dcim.models import DeviceType, Location, Manufacturer, ModuleType, RackType
from extras.choices import *
from extras.models import *
from netbox.forms import PrimaryModelBulkEditForm
from netbox.forms.mixins import ChangelogMessageMixin
from tenancy.models import Contact, ContactGroup, Tenant
from utilities.forms import BulkEditForm, add_blank_choice
from utilities.forms.fields import DynamicModelChoiceField
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import BulkEditNullBooleanSelect, DatePicker

from ..choices import AssetStatusChoices, PurchaseStatusChoices
from ..models import *

__all__ = (
    'AssetBulkEditForm',
    'AuditFlowBulkEditForm',
    'AuditFlowPageBulkEditForm',
    'AuditFlowPageAssignmentBulkEditForm',
    'AuditTrailSourceBulkEditForm',
    'DeliveryBulkEditForm',
    'InventoryItemGroupBulkEditForm',
    'PurchaseBulkEditForm',
    'SupplierBulkEditForm',
    'InventoryItemTypeBulkEditForm',
)

#
# Assets
#


class InventoryItemGroupBulkEditForm(PrimaryModelBulkEditForm):
    parent = DynamicModelChoiceField(
        queryset=InventoryItemGroup.objects.all(),
        required=False,
    )

    model = InventoryItemGroup
    fieldsets = (
        FieldSet(
            'parent',
            'description',
        ),
    )
    nullable_fields = (
        'parent',
        'description',
    )


class InventoryItemTypeBulkEditForm(PrimaryModelBulkEditForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label='Manufacturer',
    )
    inventoryitem_group = DynamicModelChoiceField(
        queryset=InventoryItemGroup.objects.all(),
        required=False,
        label='Inventory Item Group',
    )

    model = InventoryItemType
    fieldsets = (
        FieldSet(
            'manufacturer',
            'inventoryitem_group',
            'description',
            name='Inventory Item Type',
        ),
    )
    nullable_fields = (
        'inventoryitem_group',
        'description',
        'comments',
    )


class AssetBulkEditForm(PrimaryModelBulkEditForm):
    name = forms.CharField(
        required=False,
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(AssetStatusChoices),
        required=False,
        initial='',
    )
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        label='Device type',
    )
    # FIXME figure out how to only show set null checkbox
    device = forms.CharField(
        disabled=True,
        required=False,
    )
    module_type = DynamicModelChoiceField(
        queryset=ModuleType.objects.all(),
        required=False,
        label='Module type',
    )
    # FIXME figure out how to only show set null checkbox
    module = forms.CharField(
        disabled=True,
        required=False,
    )
    rack_type = DynamicModelChoiceField(
        queryset=RackType.objects.all(),
        required=False,
        label='Rack type',
    )
    # FIXME figure out how to only show set null checkbox
    rack = forms.CharField(
        disabled=True,
        required=False,
    )
    owning_tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        help_text=Asset._meta.get_field('owning_tenant').help_text,
        required=not Asset._meta.get_field('owning_tenant').blank,
    )
    purchase = DynamicModelChoiceField(
        queryset=Purchase.objects.all(),
        help_text=Asset._meta.get_field('purchase').help_text,
        required=not Asset._meta.get_field('purchase').blank,
    )
    delivery = DynamicModelChoiceField(
        queryset=Delivery.objects.all(),
        help_text=Asset._meta.get_field('delivery').help_text,
        required=not Asset._meta.get_field('delivery').blank,
    )
    warranty_start = forms.DateField(
        label='Warranty start',
        required=False,
        widget=DatePicker(),
    )
    warranty_end = forms.DateField(
        label='Warranty end',
        required=False,
        widget=DatePicker(),
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        help_text=Asset._meta.get_field('tenant').help_text,
        required=not Asset._meta.get_field('tenant').blank,
    )
    contact_group = DynamicModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        null_option='None',
        label='Contact Group',
        help_text='Filter contacts by group',
    )
    contact = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        help_text=Asset._meta.get_field('contact').help_text,
        required=not Asset._meta.get_field('contact').blank,
        query_params={
            'group_id': '$contact_group',
        },
    )
    storage_location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        help_text=Asset._meta.get_field('storage_location').help_text,
        required=False,
    )

    model = Asset
    fieldsets = (
        FieldSet(
            'name',
            'status',
            'description',
            name='General',
        ),
        FieldSet(
            'device_type',
            'device',
            'module_type',
            'module',
            'rack_type',
            'rack',
            name='Hardware',
        ),
        FieldSet(
            'owning_tenant',
            'purchase',
            'delivery',
            'warranty_start',
            'warranty_end',
            name='Purchase',
        ),
        FieldSet(
            'tenant',
            'contact_group',
            'contact',
            name='Assigned to',
        ),
        FieldSet(
            'storage_location',
            name='Location',
        ),
    )
    nullable_fields = (
        'name',
        'description',
        'device',
        'module',
        'rack',
        'owning_tenant',
        'purchase',
        'delivery',
        'tenant',
        'contact',
        'warranty_start',
        'warranty_end',
        'storage_location',
    )


#
# Deliveries
#


class SupplierBulkEditForm(PrimaryModelBulkEditForm):
    model = Supplier
    fieldsets = (
        FieldSet(
            'description',
            name='General',
        ),
    )
    nullable_fields = ('description',)


class PurchaseBulkEditForm(PrimaryModelBulkEditForm):
    status = forms.ChoiceField(
        choices=add_blank_choice(PurchaseStatusChoices),
        required=False,
        initial='',
    )
    date = forms.DateField(
        label='Date',
        required=False,
        widget=DatePicker(),
    )
    supplier = DynamicModelChoiceField(
        queryset=Supplier.objects.all(),
        required=False,
        label='Supplier',
    )

    model = Purchase
    fieldsets = (
        FieldSet(
            'date',
            'status',
            'supplier',
            'description',
            name='General',
        ),
    )
    nullable_fields = (
        'date',
        'description',
    )


class DeliveryBulkEditForm(PrimaryModelBulkEditForm):
    date = forms.DateField(
        label='Date',
        required=False,
        widget=DatePicker(),
    )
    purchase = DynamicModelChoiceField(
        queryset=Purchase.objects.all(),
        required=False,
        label='Purchase',
    )
    contact_group = DynamicModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        null_option='None',
        label='Contact Group',
        help_text='Filter receiving contacts by group',
    )
    receiving_contact = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        label='Receiving Contact',
        query_params={
            'group_id': '$contact_group',
        },
    )

    model = Delivery
    fieldsets = (
        FieldSet(
            'date',
            'purchase',
            'contact_group',
            'receiving_contact',
            'description',
            name='General',
        ),
    )
    nullable_fields = (
        'date',
        'description',
        'receiving_contact',
    )


#
# Audit
#


class AuditFlowBulkEditForm(PrimaryModelBulkEditForm):
    enabled = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect(),
    )

    model = AuditFlow

    fieldsets = (
        FieldSet(
            'enabled',
            name=_('Attributes'),
        ),
    )


class AuditFlowPageBulkEditForm(PrimaryModelBulkEditForm):
    model = AuditFlowPage

    fieldsets = (
        FieldSet(
            'description',
            name=_('Attributes'),
        ),
    )
    nullable_fields = ('description',)


class AuditFlowPageAssignmentBulkEditForm(ChangelogMessageMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=AuditFlowPageAssignment.objects.all(),
        widget=forms.MultipleHiddenInput,
    )
    weight = forms.IntegerField(
        required=False,
    )

    fieldsets = (
        FieldSet(
            'weight',
            name=_('Attributes'),
        ),
    )


class AuditTrailSourceBulkEditForm(PrimaryModelBulkEditForm):
    model = AuditTrailSource

    fieldsets = (
        FieldSet(
            'description',
            name=_('Attributes'),
        ),
    )
    nullable_fields = ('description',)
