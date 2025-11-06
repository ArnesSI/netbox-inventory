from django import forms
from django.utils.translation import gettext_lazy as _

from dcim.models import DeviceType, Location, Manufacturer, ModuleType, RackType
from extras.choices import *
from extras.models import *
from netbox.forms import NetBoxModelBulkEditForm
from netbox.forms.mixins import ChangelogMessageMixin
from tenancy.models import Contact, ContactGroup, Tenant
from utilities.forms import BulkEditForm, add_blank_choice
from utilities.forms.fields import (
    CommentField,
    DynamicModelChoiceField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import BulkEditNullBooleanSelect, DatePicker

from ..choices import AssetStatusChoices, PurchaseStatusChoices
from ..models import *

__all__ = (
    'AssetBulkEditForm',
    'AuditFlowBulkEditForm',
    'AuditFlowPageAssignmentBulkEditForm',
    'DeliveryBulkEditForm',
    'InventoryItemGroupBulkEditForm',
    'PurchaseBulkEditForm',
    'SupplierBulkEditForm',
    'InventoryItemTypeBulkEditForm',
)

#
# Assets
#


class InventoryItemGroupBulkEditForm(NetBoxModelBulkEditForm):
    parent = DynamicModelChoiceField(
        queryset=InventoryItemGroup.objects.all(),
        required=False,
    )
    description = forms.CharField(
        max_length=200,
        required=False,
    )
    comments = CommentField(
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


class InventoryItemTypeBulkEditForm(NetBoxModelBulkEditForm):
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
    description = forms.CharField(
        max_length=200,
        required=False,
    )
    comments = CommentField(
        required=False,
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


class AssetBulkEditForm(NetBoxModelBulkEditForm):
    name = forms.CharField(
        required=False,
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(AssetStatusChoices),
        required=False,
        initial='',
    )
    description = forms.CharField(
        max_length=200,
        required=False,
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
    owner = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        help_text=Asset._meta.get_field('owner').help_text,
        required=not Asset._meta.get_field('owner').blank,
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
    comments = CommentField(
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
            'owner',
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
        'owner',
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


class SupplierBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(
        required=False,
    )
    comments = CommentField(
        required=False,
    )

    model = Supplier
    fieldsets = (
        FieldSet(
            'description',
            name='General',
        ),
    )
    nullable_fields = ('description',)


class PurchaseBulkEditForm(NetBoxModelBulkEditForm):
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
    description = forms.CharField(
        required=False,
    )
    comments = CommentField(
        required=False,
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


class DeliveryBulkEditForm(NetBoxModelBulkEditForm):
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
    description = forms.CharField(
        required=False,
    )
    comments = CommentField(
        required=False,
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


class AuditFlowBulkEditForm(NetBoxModelBulkEditForm):
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
