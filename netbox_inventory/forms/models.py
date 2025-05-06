from dcim.models import DeviceType, Location, Manufacturer, ModuleType, RackType, Site
from netbox.forms import NetBoxModelForm
from tenancy.models import Contact, ContactGroup, Tenant
from utilities.forms.fields import CommentField, DynamicModelChoiceField, SlugField
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import DatePicker

from netbox_inventory.choices import HardwareKindChoices

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
from ..utils import get_tags_and_edit_protected_asset_fields

__all__ = (
    'AssetForm',
    'SupplierForm',
    'BOMForm',
    'PurchaseForm',
    'DeliveryForm',
    'InventoryItemTypeForm',
    'InventoryItemGroupForm',
    'CourierForm',
    'TransferForm',
)


class AssetForm(NetBoxModelForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        initial_params={
            "device_types": "$device_type",
            "module_types": "$module_type",
            "inventoryitem_types": "$inventoryitem_type",
            "rack_types": "$rack_type",
        },
    )
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        query_params={
            "manufacturer_id": "$manufacturer",
        },
    )
    module_type = DynamicModelChoiceField(
        queryset=ModuleType.objects.all(),
        required=False,
        query_params={
            "manufacturer_id": "$manufacturer",
        },
    )
    inventoryitem_type = DynamicModelChoiceField(
        queryset=InventoryItemType.objects.all(),
        required=False,
        query_params={
            "manufacturer_id": "$manufacturer",
        },
        label="Inventory item type",
    )
    rack_type = DynamicModelChoiceField(
        queryset=RackType.objects.all(),
        required=False,
        query_params={
            "manufacturer_id": "$manufacturer",
        },
    )
    owner = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        help_text=Asset._meta.get_field("owner").help_text,
        required=not Asset._meta.get_field("owner").blank,
    )
    bom = DynamicModelChoiceField(
        queryset=BOM.objects.all(),
        help_text=Asset._meta.get_field("bom").help_text,
        required=not Asset._meta.get_field("bom").blank,
        label="BOM",
    )
    purchase = DynamicModelChoiceField(
        queryset=Purchase.objects.all(),
        help_text=Asset._meta.get_field("purchase").help_text,
        required=not Asset._meta.get_field("purchase").blank,
    )
    delivery = DynamicModelChoiceField(
        queryset=Delivery.objects.all(),
        help_text=Asset._meta.get_field("delivery").help_text,
        required=not Asset._meta.get_field("delivery").blank,
        query_params={"purchase_id": "$purchase"},
    )
    transfer = DynamicModelChoiceField(
        queryset=Transfer.objects.all(),
        help_text=Asset._meta.get_field('transfer').help_text,
        required=not Asset._meta.get_field('transfer').blank,
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        help_text=Asset._meta.get_field("tenant").help_text,
        required=not Asset._meta.get_field("tenant").blank,
    )
    contact_group = DynamicModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        null_option="None",
        label="Contact Group",
        help_text="Filter contacts by group",
        initial_params={
            "contacts": "$contact",
        },
    )
    contact = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        help_text=Asset._meta.get_field("contact").help_text,
        required=not Asset._meta.get_field("contact").blank,
        query_params={
            "group_id": "$contact_group",
        },
    )
    storage_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        initial_params={
            "locations": "$storage_location",
        },
    )
    storage_location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        help_text=Asset._meta.get_field("storage_location").help_text,
        required=False,
        query_params={
            "site_id": "$storage_site",
        },
    )
    comments = CommentField()

    fieldsets = (
        FieldSet("name", "asset_tag", "description", "tags", "status", name="General"),
        FieldSet(
            "serial",
            "manufacturer",
            "device_type",
            "module_type",
            "inventoryitem_type",
            "rack_type",
            name="Hardware",
        ),
        FieldSet(
            'owner',
            'bom',
            'purchase',
            'delivery',
            'transfer',
            'warranty_start',
            'warranty_end',
            name='Purchase',
        ),
        FieldSet("tenant", "contact_group", "contact", name="Assigned to"),
        FieldSet("storage_site", "storage_location", name="Location"),
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
            'bom',
            'purchase',
            'delivery',
            'transfer',
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
            "warranty_start": DatePicker(),
            "warranty_end": DatePicker(),
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
            self.fields["manufacturer"].disabled = True
            for kind in HardwareKindChoices.values():
                self.fields[f"{kind}_type"].disabled = True

    def _disable_fields_by_tags(self):
        """
        We need to disable fields that are not editable based on the tags that are assigned to the asset.
        """
        if not self.instance.pk:
            # If we are creating a new asset we can't disable fields
            return

        # Disable fields that should not be edited
        tags = self.instance.tags.all().values_list("slug", flat=True)
        tags_and_disabled_fields = get_tags_and_edit_protected_asset_fields()

        for tag in tags:
            if tag not in tags_and_disabled_fields:
                continue

            for field in tags_and_disabled_fields[tag]:
                if field in self.fields:
                    self.fields[field].disabled = True

    def clean(self):
        super().clean()
        # if only delivery set, infer pruchase from it
        delivery = self.cleaned_data["delivery"]
        purchase = self.cleaned_data["purchase"]
        if delivery and not purchase:
            self.cleaned_data['purchase'] = delivery.purchases.first()


class SupplierForm(NetBoxModelForm):
    slug = SlugField(slug_source="name")
    comments = CommentField()

    fieldsets = (FieldSet("name", "slug", "description", "tags", name="Supplier"),)

    class Meta:
        model = Supplier
        fields = (
            "name",
            "slug",
            "description",
            "comments",
            "tags",
        )


class BOMForm(NetBoxModelForm):
    comments = CommentField()

    fieldsets = (FieldSet('name', 'status', 'description', 'tags', name='BOM'),)

    class Meta:
        model = BOM
        fields = (
            "name",
            "status",
            "description",
            "comments",
            "tags",
        )


class PurchaseForm(NetBoxModelForm):
    comments = CommentField()

    fieldsets = (
        FieldSet(
            'supplier',
            'boms',
            'name',
            'status',
            'date',
            'description',
            'tags',
            name='Purchase',
        ),
    )

    class Meta:
        model = Purchase
        fields = (
            "supplier",
            "boms",
            "name",
            "status",
            "date",
            "description",
            "comments",
            "tags",
        )
        widgets = {
            "date": DatePicker(),
        }


class DeliveryForm(NetBoxModelForm):
    delivery_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        initial_params={
            'locations': '$delivery_location',
        },
    )
    delivery_location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        help_text=Delivery._meta.get_field('delivery_location').help_text,
        required=False,
        query_params={
            'site_id': '$delivery_site',
        },
    )
    contact_group = DynamicModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        null_option="None",
        label="Contact Group",
        help_text="Filter receiving contacts by group",
        initial_params={
            "contacts": "$receiving_contact",
        },
    )
    receiving_contact = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        help_text=Delivery._meta.get_field("receiving_contact").help_text,
        query_params={
            "group_id": "$contact_group",
        },
    )

    comments = CommentField()

    fieldsets = (
        FieldSet(
            'purchases',
            'name',
            'date',
            'contact_group',
            'receiving_contact',
            'description',
            'tags',
            name='Delivery',
        ),
        FieldSet('delivery_site', 'delivery_location', name='Location'),
    )

    class Meta:
        model = Delivery
        fields = (
            'purchases',
            'name',
            'date',
            'delivery_site',
            'delivery_location',
            'contact_group',
            'receiving_contact',
            'description',
            'comments',
            'tags',
        )
        widgets = {
            "date": DatePicker(),
        }


class InventoryItemTypeForm(NetBoxModelForm):
    slug = SlugField(slug_source="model")
    inventoryitem_group = DynamicModelChoiceField(
        queryset=InventoryItemGroup.objects.all(),
        required=False,
        label="Inventory item group",
    )
    comments = CommentField()

    fieldsets = (
        FieldSet(
            "manufacturer",
            "model",
            "slug",
            "description",
            "part_number",
            "inventoryitem_group",
            "tags",
            name="Inventory Item Type",
        ),
    )

    class Meta:
        model = InventoryItemType
        fields = (
            "manufacturer",
            "model",
            "slug",
            "description",
            "part_number",
            "inventoryitem_group",
            "tags",
            "comments",
        )


class InventoryItemGroupForm(NetBoxModelForm):
    parent = DynamicModelChoiceField(
        queryset=InventoryItemGroup.objects.all(),
        required=False,
        label="Parent",
    )
    comments = CommentField()

    fieldsets = (
        FieldSet("name", "parent", "description", "tags", name="Inventory Item Group"),
    )

    class Meta:
        model = InventoryItemGroup
        fields = (
            "name",
            "parent",
            "description",
            "tags",
            "comments",
        )


class CourierForm(NetBoxModelForm):
    slug = SlugField(slug_source='name')
    comments = CommentField()

    fieldsets = (FieldSet('name', 'slug', 'description', 'tags', name='Supplier'),)

    class Meta:
        model = Courier
        fields = (
            'name',
            'slug',
            'description',
            'comments',
            'tags',
        )


class TransferForm(NetBoxModelForm):
    sender_group = DynamicModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        null_option='None',
        label='Sender Group',
        help_text='Filter senders by group',
        initial_params={
            'contacts': '$sender',
        },
    )
    sender = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        help_text=Transfer._meta.get_field('sender').help_text,
        required=not Transfer._meta.get_field('sender').blank,
        query_params={
            'group_id': '$sender_group',
        },
    )
    recipient_group = DynamicModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        null_option='None',
        label='Recipient Group',
        help_text='Filter recipients by group',
        initial_params={
            'contacts': '$recipient',
        },
    )
    recipient = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        help_text=Transfer._meta.get_field('recipient').help_text,
        required=not Transfer._meta.get_field('recipient').blank,
        query_params={
            'group_id': '$recipient_group',
        },
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        help_text=Transfer._meta.get_field('site').help_text,
        required=True,
        initial_params={
            'locations': '$location',
        },
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        help_text=Transfer._meta.get_field('location').help_text,
        required=False,
        query_params={
            'site_id': '$site',
        },
    )
    comments = CommentField()

    fieldsets = (
        FieldSet(
            'name',
            'courier',
            'shipping_number',
            'instructions',
            'status',
            name='General',
        ),
        FieldSet(
            'sender',
            'recipient',
            'site',
            'location',
            'pickup_date',
            'received_date',
            'tags',
            name='Transfer',
        ),
    )

    class Meta:
        model = Transfer
        fields = (
            'name',
            'courier',
            'shipping_number',
            'instructions',
            'status',
            'sender',
            'recipient',
            'site',
            'location',
            'pickup_date',
            'received_date',
            'tags',
            'comments',
        )
        widgets = {
            'pickup_date': DatePicker(),
            'received_date': DatePicker(),
        }
