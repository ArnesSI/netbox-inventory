from django.utils.translation import gettext_lazy as _

from core.models import ObjectType
from dcim.models import DeviceType, Location, Manufacturer, ModuleType, RackType, Site
from netbox.forms import NetBoxModelForm
from tenancy.models import Contact, ContactGroup, Tenant
from utilities.forms.fields import (
    CommentField,
    ContentTypeChoiceField,
    DynamicModelChoiceField,
    JSONField,
    SlugField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import DatePicker

from ..constants import AUDITFLOW_OBJECT_TYPE_CHOICES
from ..models import *
from ..utils import get_tags_and_edit_protected_asset_fields
from netbox_inventory.choices import HardwareKindChoices

__all__ = (
    'AssetForm',
    'AuditFlowForm',
    'AuditFlowPageAssignmentForm',
    'AuditFlowPageForm',
    'AuditTrailSourceForm',
    'DeliveryForm',
    'InventoryItemGroupForm',
    'InventoryItemTypeForm',
    'PurchaseForm',
    'SupplierForm',
)


#
# Assets
#


class InventoryItemGroupForm(NetBoxModelForm):
    parent = DynamicModelChoiceField(
        queryset=InventoryItemGroup.objects.all(),
        required=False,
        label='Parent',
    )
    comments = CommentField()

    fieldsets = (
        FieldSet(
            'name',
            'parent',
            'description',
            'tags',
            name='Inventory Item Group',
        ),
    )

    class Meta:
        model = InventoryItemGroup
        fields = (
            'name',
            'parent',
            'description',
            'tags',
            'comments',
        )


class InventoryItemTypeForm(NetBoxModelForm):
    slug = SlugField(slug_source='model')
    inventoryitem_group = DynamicModelChoiceField(
        queryset=InventoryItemGroup.objects.all(),
        required=False,
        label='Inventory item group',
    )
    comments = CommentField()

    fieldsets = (
        FieldSet(
            'manufacturer',
            'model',
            'slug',
            'description',
            'part_number',
            'inventoryitem_group',
            'tags',
            name='Inventory Item Type',
        ),
    )

    class Meta:
        model = InventoryItemType
        fields = (
            'manufacturer',
            'model',
            'slug',
            'description',
            'part_number',
            'inventoryitem_group',
            'tags',
            'comments',
        )


class AssetForm(NetBoxModelForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        initial_params={
            'device_types': '$device_type',
            'module_types': '$module_type',
            'inventoryitem_types': '$inventoryitem_type',
            'rack_types': '$rack_type',
        },
    )
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer',
        },
    )
    module_type = DynamicModelChoiceField(
        queryset=ModuleType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer',
        },
    )
    inventoryitem_type = DynamicModelChoiceField(
        queryset=InventoryItemType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer',
        },
        label='Inventory item type',
    )
    rack_type = DynamicModelChoiceField(
        queryset=RackType.objects.all(),
        required=False,
        query_params={
            'manufacturer_id': '$manufacturer',
        },
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
        query_params={'purchase_id': '$purchase'},
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
        initial_params={
            'contact': '$contact',
        },
    )
    contact = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        help_text=Asset._meta.get_field('contact').help_text,
        required=not Asset._meta.get_field('contact').blank,
        query_params={
            'group_id': '$contact_group',
        },
    )
    storage_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        initial_params={
            'locations': '$storage_location',
        },
    )
    storage_location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        help_text=Asset._meta.get_field('storage_location').help_text,
        required=False,
        query_params={
            'site_id': '$storage_site',
        },
    )
    comments = CommentField()

    fieldsets = (
        FieldSet('name', 'asset_tag', 'description', 'tags', 'status', name='General'),
        FieldSet(
            'serial',
            'manufacturer',
            'device_type',
            'module_type',
            'inventoryitem_type',
            'rack_type',
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
        FieldSet('tenant', 'contact_group', 'contact', name='Assigned to'),
        FieldSet('storage_site', 'storage_location', name='Location'),
    )

    class Meta:
        model = Asset
        fields = (
            'name',
            'asset_tag',
            'serial',
            'status',
            'manufacturer',
            'device_type',
            'module_type',
            'inventoryitem_type',
            'rack_type',
            'storage_location',
            'owner',
            'purchase',
            'delivery',
            'warranty_start',
            'warranty_end',
            'tenant',
            'contact_group',
            'contact',
            'tags',
            'description',
            'comments',
            'storage_site',
        )
        widgets = {
            'warranty_start': DatePicker(),
            'warranty_end': DatePicker(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._disable_fields_by_tags()

        # Used for picking the default active tab for hardware type selection
        self.no_hardware_type = True
        if self.instance:
            if (
                self.instance.device_type
                or self.instance.module_type
                or self.instance.inventoryitem_type
                or self.instance.rack_type
            ):
                self.no_hardware_type = False

        # if assigned to device/module/... we can't change device_type/...
        if (
            self.instance.device
            or self.instance.module
            or self.instance.inventoryitem
            or self.instance.rack
        ):
            self.fields['manufacturer'].disabled = True
            for kind in HardwareKindChoices.values():
                self.fields[f'{kind}_type'].disabled = True

    def _disable_fields_by_tags(self):
        """
        We need to disable fields that are not editable based on the tags that are assigned to the asset.
        """
        if not self.instance.pk:
            # If we are creating a new asset we can't disable fields
            return

        # Disable fields that should not be edited
        tags = self.instance.tags.all().values_list('slug', flat=True)
        tags_and_disabled_fields = get_tags_and_edit_protected_asset_fields()

        for tag in tags:
            if tag not in tags_and_disabled_fields:
                continue

            for field in tags_and_disabled_fields[tag]:
                if field in self.fields:
                    self.fields[field].disabled = True

    def clean(self):
        super().clean()
        # if only delivery set, infer purchase from it
        delivery = self.cleaned_data['delivery']
        purchase = self.cleaned_data['purchase']
        if delivery and not purchase:
            self.cleaned_data['purchase'] = delivery.purchase


#
# Deliveries
#


class SupplierForm(NetBoxModelForm):
    slug = SlugField(slug_source='name')
    comments = CommentField()

    fieldsets = (FieldSet('name', 'slug', 'description', 'tags', name='Supplier'),)

    class Meta:
        model = Supplier
        fields = (
            'name',
            'slug',
            'description',
            'comments',
            'tags',
        )


class PurchaseForm(NetBoxModelForm):
    comments = CommentField()

    fieldsets = (
        FieldSet(
            'supplier', 'name', 'status', 'date', 'description', 'tags', name='Purchase'
        ),
    )

    class Meta:
        model = Purchase
        fields = (
            'supplier',
            'name',
            'status',
            'date',
            'description',
            'comments',
            'tags',
        )
        widgets = {
            'date': DatePicker(),
        }


class DeliveryForm(NetBoxModelForm):
    contact_group = DynamicModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        null_option='None',
        label='Contact Group',
        help_text='Filter receiving contacts by group',
        initial_params={
            'contact': '$receiving_contact',
        },
    )
    receiving_contact = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        help_text=Delivery._meta.get_field('receiving_contact').help_text,
        query_params={
            'group_id': '$contact_group',
        },
    )

    comments = CommentField()

    fieldsets = (
        FieldSet(
            'purchase',
            'name',
            'date',
            'contact_group',
            'receiving_contact',
            'description',
            'tags',
            name='Delivery',
        ),
    )

    class Meta:
        model = Delivery
        fields = (
            'purchase',
            'name',
            'date',
            'contact_group',
            'receiving_contact',
            'description',
            'comments',
            'tags',
        )
        widgets = {
            'date': DatePicker(),
        }


#
# Audit
#


class BaseFlowForm(NetBoxModelForm):
    """
    Internal base form class for audit flow models.
    """

    object_type = ContentTypeChoiceField(
        queryset=ObjectType.objects.public(),
    )
    object_filter = JSONField(
        required=False,
        help_text=_(
            'Enter object filter in <a href="https://json.org/">JSON</a> format, '
            'mapping attributes to values.'
        ),
    )
    comments = CommentField()

    fieldsets = (
        FieldSet(
            'name',
            'description',
            'tags',
        ),
        FieldSet(
            'object_type',
            'object_filter',
            name=_('Assignment'),
        ),
    )

    class Meta:
        fields = (
            'name',
            'description',
            'tags',
            'object_type',
            'object_filter',
            'comments',
        )


class AuditFlowPageForm(BaseFlowForm):
    class Meta(BaseFlowForm.Meta):
        model = AuditFlowPage


class AuditFlowForm(BaseFlowForm):
    # Restrict inherited object_type to those object types that represent physical
    # locations.
    object_type = ContentTypeChoiceField(
        queryset=ObjectType.objects.public(),
        limit_choices_to=AUDITFLOW_OBJECT_TYPE_CHOICES,
    )

    fieldsets = (
        FieldSet(
            'name',
            'description',
            'tags',
            'enabled',
        ),
        FieldSet(
            'object_type',
            'object_filter',
            name=_('Assignment'),
        ),
    )

    class Meta(BaseFlowForm.Meta):
        model = AuditFlow
        fields = BaseFlowForm.Meta.fields + ('enabled',)


class AuditFlowPageAssignmentForm(NetBoxModelForm):
    fieldsets = (
        FieldSet(
            'flow',
            'page',
            'weight',
        ),
    )

    class Meta:
        model = AuditFlowPageAssignment
        fields = (
            'flow',
            'page',
            'weight',
        )


class AuditTrailSourceForm(NetBoxModelForm):
    slug = SlugField()
    comments = CommentField()

    fieldsets = (
        FieldSet(
            'name',
            'slug',
            'description',
        ),
    )

    class Meta:
        model = AuditTrailSource
        fields = (
            'name',
            'slug',
            'description',
            'comments',
        )
