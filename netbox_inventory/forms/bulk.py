from dcim.models import DeviceType, Location, Manufacturer, ModuleType, RackType, Site
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelImportForm
from tenancy.models import Contact, ContactGroup, Tenant
from utilities.forms import add_blank_choice
from utilities.forms.fields import (
    CommentField,
    CSVChoiceField,
    CSVModelChoiceField,
    CSVModelMultipleChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
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
from ..utils import get_plugin_setting
from .fields import BigTextField
from .models import AssetForm

__all__ = (
    "AssetBulkAddForm",
    "AssetBulkAddModelForm",
    "AssetBulkEditForm",
    "AssetBulkScanForm",
    "AssetImportForm",
    "SupplierImportForm",
    "SupplierBulkEditForm",
    "BOMImportForm",
    "BOMBulkEditForm",
    "PurchaseImportForm",
    "PurchaseBulkEditForm",
    "DeliveryImportForm",
    "DeliveryBulkEditForm",
    "InventoryItemTypeImportForm",
    "InventoryItemTypeBulkEditForm",
    "InventoryItemGroupImportForm",
    "InventoryItemGroupBulkEditForm",
    'CourierImportForm',
    'CourierBulkEditForm',
    'TransferImportForm',
    'TransferBulkEditForm',
)


class AssetBulkAddForm(forms.Form):
    """Form for creating multiple Assets by count"""

    count = forms.IntegerField(
        min_value=1,
        required=True,
        help_text="How many assets to create",
    )


class AssetBulkAddModelForm(AssetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["asset_tag"].disabled = True
        self.fields["serial"].disabled = True


class AssetBulkAddForm(forms.Form):
    """Form for creating multiple Assets by count"""

    count = forms.IntegerField(
        min_value=1,
        required=True,
        help_text="How many assets to create",
    )


class AssetBulkAddModelForm(AssetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["asset_tag"].disabled = True
        self.fields["serial"].disabled = True


class AssetBulkEditForm(NetBoxModelBulkEditForm):
    name = forms.CharField(
        required=False,
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(AssetStatusChoices),
        required=False,
        initial="",
    )
    description = forms.CharField(max_length=200, required=False)
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        required=False,
        label="Device type",
    )
    # FIXME figure out how to only show set null checkbox
    device = forms.CharField(
        disabled=True,
        required=False,
    )
    module_type = DynamicModelChoiceField(
        queryset=ModuleType.objects.all(),
        required=False,
        label="Module type",
    )
    # FIXME figure out how to only show set null checkbox
    module = forms.CharField(
        disabled=True,
        required=False,
    )
    rack_type = DynamicModelChoiceField(
        queryset=RackType.objects.all(),
        required=False,
        label="Rack type",
    )
    # FIXME figure out how to only show set null checkbox
    rack = forms.CharField(
        disabled=True,
        required=False,
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
    )
    transfer = DynamicModelChoiceField(
        queryset=Transfer.objects.all(),
        help_text=Asset._meta.get_field('transfer').help_text,
        required=not Asset._meta.get_field('transfer').blank,
    )
    warranty_start = forms.DateField(
        label="Warranty start", required=False, widget=DatePicker()
    )
    warranty_end = forms.DateField(
        label="Warranty end", required=False, widget=DatePicker()
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
    )
    contact = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        help_text=Asset._meta.get_field("contact").help_text,
        required=not Asset._meta.get_field("contact").blank,
        query_params={
            "group_id": "$contact_group",
        },
    )
    storage_location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        help_text=Asset._meta.get_field("storage_location").help_text,
        required=False,
    )
    comments = CommentField(
        required=False,
    )

    model = Asset
    fieldsets = (
        FieldSet("name", "status", "description", name="General"),
        FieldSet(
            "device_type",
            "device",
            "module_type",
            "module",
            "rack_type",
            "rack",
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
        FieldSet("storage_location", name="Location"),
    )
    nullable_fields = (
        "name",
        "description",
        "device",
        "module",
        "rack",
        "owner",
        "bom",
        "purchase",
        "delivery",
        "transfer",
        "tenant",
        "contact",
        "warranty_start",
        "warranty_end",
    )


class AssetBulkScanForm(forms.Form):
    serial_numbers = BigTextField(
        required=True,
        help_text="Scan barcode or manually enter serial numbers.",
        label="Serial numbers",
    )

    # asset_tags = BigTextField(
    #     required=True,
    #     help_text='Scan or manually enter asset tags.',
    #     label='Asset tags',
    # )

    pk = forms.ModelMultipleChoiceField(
        queryset=None, widget=forms.MultipleHiddenInput  # Set from self.model on init
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["pk"].queryset = self.model.objects.all()

    model = Asset


class AssetImportForm(NetBoxModelImportForm):
    hardware_kind = CSVChoiceField(
        choices=HardwareKindChoices,
        required=True,
        help_text="What kind of hardware is this.",
    )
    manufacturer = CSVModelChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name="name",
        required=True,
        help_text="Hardware manufacturer.",
    )
    model_name = forms.CharField(
        required=True,
        help_text='Model of this device/module/inventory item/rack type. See "Import settings" for more info.',
    )
    part_number = forms.CharField(
        required=False,
        help_text="Discrete part number for model. Only used if creating new model.",
    )
    model_description = forms.CharField(
        required=False,
        help_text="Description for model. Only used if creating new model.",
    )
    model_comments = forms.CharField(
        required=False,
        help_text="Comments for model. Only used if creating new model.",
    )
    status = CSVChoiceField(
        choices=AssetStatusChoices,
        help_text="Asset lifecycle status.",
    )
    storage_site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name="name",
        help_text="Site that contains storage_location asset will be stored in.",
        required=False,
    )
    storage_location = CSVModelChoiceField(
        queryset=Location.objects.all(),
        to_field_name="name",
        help_text="Location where is this asset stored when not in use. It must exist before import.",
        required=False,
    )
    owner = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        help_text="Tenant that owns this asset. It must exist before import.",
        required=False,
    )
    bom = CSVModelChoiceField(
        queryset=BOM.objects.all(),
        to_field_name="name",
        help_text="BOM that this asset is part of. It must exist before import.",
        required=False,
    )
    delivery = forms.CharField(
        help_text='Delivery that delivered this asset. See "Import settings" for more info.',
        required=False,
    )
    delivery_date = forms.DateField(
        help_text="Date when this delivery was made.",
        required=False,
    )
    receiving_contact = CSVModelChoiceField(
        queryset=Contact.objects.all(),
        to_field_name="name",
        help_text="Contact that accepted this delivery. It must exist before import.",
        required=False,
    )
    purchase = forms.CharField(
        help_text='Purchase through which this asset was purchased. See "Import settings" for more info.',
        required=False,
    )
    purchase_date = forms.DateField(
        help_text="Date when this purchase was made.",
        required=False,
    )
    purchase_status = CSVChoiceField(
        choices=PurchaseStatusChoices, help_text="Status of purchase", required=False
    )
    supplier = CSVModelChoiceField(
        queryset=Supplier.objects.all(),
        to_field_name="name",
        help_text="Legal entity this purchase was made from. Required if a new purchase is given.",
        required=False,
    )
    transfer = CSVModelChoiceField(
        queryset=Transfer.objects.all(),
        to_field_name='name',
        help_text='Transfer this asset is part of. It must exist before import.',
        required=False,
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name="name",
        help_text='Tenant using this asset. See "Import settings" for more info.',
        required=False,
    )
    contact = CSVModelChoiceField(
        queryset=Contact.objects.all(),
        to_field_name="name",
        help_text="Contact using this asset. It must exist before import.",
        required=False,
    )

    class Meta:
        model = Asset
        fields = (
            "name",
            "asset_tag",
            "serial",
            "status",
            "description",
            "hardware_kind",
            "manufacturer",
            "model_name",
            "part_number",
            "model_description",
            "model_comments",
            "storage_site",
            "storage_location",
            "owner",
            "supplier",
            "bom",
            "purchase",
            "purchase_date",
            "purchase_status",
            "delivery",
            "delivery_date",
            "receiving_contact",
            "transfer",
            "warranty_start",
            "warranty_end",
            "comments",
            "tenant",
            "contact",
            "tags",
        )

    def clean_model_name(self):
        hardware_kind = self.cleaned_data.get("hardware_kind")
        manufacturer = self.cleaned_data.get("manufacturer")
        model = self.cleaned_data.get("model_name")
        if not hardware_kind or not manufacturer:
            # clean on manufacturer or hardware_kind already raises
            return None
        if hardware_kind == "device":
            hardware_class = DeviceType
        elif hardware_kind == "module":
            hardware_class = ModuleType
        elif hardware_kind == "inventoryitem":
            hardware_class = InventoryItemType
        elif hardware_kind == "rack":
            hardware_class = RackType
        try:
            hardware_type = hardware_class.objects.get(
                manufacturer=manufacturer, model=model
            )
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                f'Hardware type not found: "{hardware_kind}", "{manufacturer}", "{model}"'
            )
        setattr(self.instance, f"{hardware_kind}_type", hardware_type)
        return hardware_type

    def clean_purchase(self):
        supplier = self.cleaned_data.get("supplier")
        purchase_name = self.cleaned_data.get("purchase")
        if not purchase_name:
            return None
        try:
            purchase = Purchase.objects.get(supplier=supplier, name=purchase_name)
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                f"Unable to find purchase {supplier} {purchase_name}"
            )
        return purchase

    def clean_delivery(self):
        purchase = self.cleaned_data.get("purchase")
        delivery_name = self.cleaned_data.get("delivery")
        if not delivery_name:
            return None
        try:
            delivery = Delivery.objects.get(name=delivery_name)
            delivery.purchases.set([purchase])
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                f"Unable to find delivery {purchase} {delivery_name}"
            )
        return delivery

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:
            # filter storage_location queryset on selected storage_site
            params = {
                f'site__{self.fields["storage_site"].to_field_name}': data.get(
                    "storage_site"
                )
            }
            self.fields["storage_location"].queryset = self.fields[
                "storage_location"
            ].queryset.filter(**params)

    def _clean_fields(self):
        """
        _clean_fields is the first step where form cleanup and validation takes place.
        We use this point to analyze CSV data and create related objects if needed.
        Last we call super()._clean_fields and form validation continues as usual.
        """
        self._create_related_objects()
        return super()._clean_fields()

    def _get_validation_exclusions(self):
        """
        Form's validate_unique calls this method to determine what atributes to
        exclude from uniqness check. Parent method excludes any fields that are
        not present on form. In our case we have model_name field we assign to
        device_type, module_type, inventoryitem_type or rack_type dinamically.
        So we remove those fields from exclusions.
        """
        exclude = super()._get_validation_exclusions()
        exclude.remove("device_type")
        exclude.remove("module_type")
        exclude.remove("inventoryitem_type")
        exclude.remove("rack_type")
        return exclude

    def _create_related_objects(self):  # noqa: C901
        """
        Create missing related objects (Purchase, DeviceType...). Based on plugin
        settings.
        On exceptions we add to form errors so user gets correct feedback that
        something is wrong.
        """
        try:
            # handle creating related resources if they don't exist and enabled in settings
            if (
                get_plugin_setting("asset_import_create_purchase")
                and self.data.get("purchase")
                and self.data.get("supplier")
            ):
                purchase, _ = Purchase.objects.get_or_create(
                    name=self.data.get("purchase"),
                    supplier=self._get_or_create_related("supplier"),
                    defaults={
                        "date": self._get_clean_value("purchase_date"),
                        "status": self._get_clean_value("purchase_status"),
                    },
                )
                if self.data.get("delivery"):
                    Delivery.objects.get_or_create(
                        name=self.data.get("delivery"),
                        purchase=purchase,
                        defaults={
                            "date": self._get_clean_value("delivery_date"),
                            "receiving_contact": self._get_clean_value(
                                "receiving_contact"
                            ),
                        },
                    )
            if (
                get_plugin_setting("asset_import_create_device_type")
                and self.data.get("hardware_kind") == "device"
            ):
                DeviceType.objects.get_or_create(
                    model__iexact=self.data.get("model_name"),
                    manufacturer=self._get_or_create_related("manufacturer"),
                    defaults={
                        "model": self.data.get("model_name"),
                        "slug": slugify(self.data.get("model_name")),
                        "part_number": self._get_clean_value("part_number"),
                        "description": self._get_clean_value("model_description"),
                        "comments": self._get_clean_value("model_comments"),
                    },
                )
            if (
                get_plugin_setting("asset_import_create_module_type")
                and self.data.get("hardware_kind") == "module"
            ):
                ModuleType.objects.get_or_create(
                    model__iexact=self.data.get("model_name"),
                    manufacturer=self._get_or_create_related("manufacturer"),
                    defaults={
                        "model": self.data.get("model_name"),
                        "part_number": self._get_clean_value("part_number"),
                        "description": self._get_clean_value("model_description"),
                        "comments": self._get_clean_value("model_comments"),
                    },
                )
            if (
                get_plugin_setting("asset_import_create_inventoryitem_type")
                and self.data.get("hardware_kind") == "inventoryitem"
            ):
                InventoryItemType.objects.get_or_create(
                    model__iexact=self.data.get("model_name"),
                    manufacturer=self._get_or_create_related("manufacturer"),
                    defaults={
                        "model": self.data.get("model_name"),
                        "slug": slugify(self.data.get("model_name")),
                        "part_number": self._get_clean_value("part_number"),
                        "description": self._get_clean_value("model_description"),
                        "comments": self._get_clean_value("model_comments"),
                    },
                )
            if (
                get_plugin_setting("asset_import_create_rack_type")
                and self.data.get("hardware_kind") == "rack"
            ):
                RackType.objects.get_or_create(
                    model__iexact=self.data.get("model_name"),
                    manufacturer=self._get_or_create_related("manufacturer"),
                    defaults={
                        "model": self.data.get("model_name"),
                        "slug": slugify(self.data.get("model_name")),
                        "description": self._get_clean_value("model_description"),
                        "comments": self._get_clean_value("model_comments"),
                    },
                )
            if get_plugin_setting("asset_import_create_tenant") and self.data.get(
                "tenant"
            ):
                self._get_or_create_related("tenant")
            if get_plugin_setting("asset_import_create_tenant") and self.data.get(
                "owner"
            ):
                self._get_or_create_related("owner")
        except forms.ValidationError:
            # ValidationErrors are raised by _clean_fields() method
            # this will be called later in the code and will be bound
            # to correct field. So we skiup this kinds of errors here.
            pass
        except Exception as e:
            # any other errors we add to non-field specific form errors
            self.add_error(None, e)

    def _get_or_create_related(self, field_name):
        """
        Create instance of related object if it doesn't exist.
        Supports specifiying related object by name or slug.
        """
        klass = self.fields[field_name].queryset.model
        # user could have specified alternative field (tenant name or tenant slug)
        to_field_name = self.fields[field_name].to_field_name
        # create sensible default data if we'll need to create object
        instance_defaults = {
            "name": self.data.get(field_name),
            "slug": slugify(self.data.get(field_name)),
        }
        # whatever field was in import data is used as is
        instance_defaults.update({to_field_name: self.data.get(field_name)})
        instance, _ = klass.objects.get_or_create(
            # filter on field specified in column header
            **{to_field_name + "__iexact": self.data.get(field_name)},
            defaults=instance_defaults,
        )
        return instance

    def _get_clean_value(self, field_name):
        """
        Returns cleaned value for a given field from self.data
        Used when creating additional related objects on import, since the values
        are otherwise not validated by forms.
        Used for DateTime, Boolean and similar fields. If used on ModelField and
        instance does not exist it raises Exception but no feedback is given to user.
        """
        try:
            return self.base_fields[field_name].clean(self.data.get(field_name))
        except forms.ValidationError as e:
            self.add_error(field_name, e)
            raise


class SupplierImportForm(NetBoxModelImportForm):
    class Meta:
        model = Supplier
        fields = ("name", "slug", "description", "comments", "tags")


class SupplierBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(
        required=False,
    )
    comments = CommentField(
        required=False,
    )

    model = Supplier
    fieldsets = (FieldSet("description", name="General"),)
    nullable_fields = ("description",)


class BOMImportForm(NetBoxModelImportForm):
    status = CSVChoiceField(
        choices=BOMStatusChoices,
        help_text="Status of BOM",
    )

    class Meta:
        model = Purchase
        fields = (
            "name",
            "status",
            "description",
            "comments",
            "tags",
        )


class BOMBulkEditForm(NetBoxModelBulkEditForm):
    status = forms.ChoiceField(
        choices=add_blank_choice(BOMStatusChoices),
        required=False,
        initial="",
    )
    description = forms.CharField(
        required=False,
    )
    comments = CommentField(
        required=False,
    )

    model = BOM
    fieldsets = (FieldSet("status", "description", name="General"),)
    nullable_fields = ("description",)


class PurchaseImportForm(NetBoxModelImportForm):
    supplier = CSVModelChoiceField(
        queryset=Supplier.objects.all(),
        to_field_name="name",
        help_text="Legal entity this purchase was made at. It must exist when importing.",
        required=True,
    )
    boms = CSVModelMultipleChoiceField(
        queryset=BOM.objects.all(),
        to_field_name="name",
        help_text='BOM names separated by commas, encased with double quotes (e.g. "BOM1,BOM2,BOM3")',
        required=False,
        label="BOMs",
    )
    status = CSVChoiceField(
        choices=PurchaseStatusChoices,
        help_text="Status of purchase",
    )

    class Meta:
        model = Purchase
        fields = (
            "name",
            "date",
            "status",
            "supplier",
            "boms",
            "description",
            "comments",
            "tags",
        )


class PurchaseBulkEditForm(NetBoxModelBulkEditForm):
    status = forms.ChoiceField(
        choices=add_blank_choice(PurchaseStatusChoices),
        required=False,
        initial="",
    )
    date = forms.DateField(label="Date", required=False, widget=DatePicker())
    supplier = DynamicModelChoiceField(
        queryset=Supplier.objects.all(),
        required=False,
        label="Supplier",
    )
    boms = DynamicModelMultipleChoiceField(
        queryset=BOM.objects.all(),
        required=False,
        label="BOMs",
    )
    description = forms.CharField(
        required=False,
    )
    comments = CommentField(
        required=False,
    )

    model = Purchase
    fieldsets = (
        FieldSet("date", "status", "supplier", "boms", "description", name="General"),
    )
    nullable_fields = (
        "date",
        "boms",
        "description",
    )


class DeliveryImportForm(NetBoxModelImportForm):
    purchases = CSVModelMultipleChoiceField(
        queryset=Purchase.objects.all(),
        to_field_name="id",
        help_text="Purchase that this delivery is part of. It must exist when importing.",
        required=True,
    )
    delivery_site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text='Site that contains delivery_location where delivery will be received.',
        required=False,
    )
    delivery_location = CSVModelChoiceField(
        queryset=Location.objects.all(),
        to_field_name='name',
        help_text='Location where this delivery is to be received. It must exist before import.',
        required=False,
    )
    receiving_contact = CSVModelChoiceField(
        queryset=Contact.objects.all(),
        to_field_name="id",
        help_text="Contact that accepted this delivery. It must exist when importing.",
        required=False,
    )

    class Meta:
        model = Delivery
        fields = (
            "name",
            "date",
            "purchases",
            "delivery_site",
            "delivery_location",
            "receiving_contact",
            "description",
            "comments",
            "tags",
        )


class DeliveryBulkEditForm(NetBoxModelBulkEditForm):
    date = forms.DateField(label='Date', required=False, widget=DatePicker())
    purchases = DynamicModelMultipleChoiceField(
        queryset=Purchase.objects.all(),
        required=False,
        label='Purchases',
    )
    delivery_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        null_option='None',
        label='Delivery Site',
        help_text='Filter delivery locations by site',
    )
    delivery_location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        help_text=Delivery._meta.get_field('delivery_location').help_text,
        label='Delivery Location',
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
    )
    receiving_contact = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        required=False,
        label="Receiving Contact",
        query_params={
            "group_id": "$contact_group",
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
            "date",
            "purchases",
            "contact_group",
            "receiving_contact",
            "description",
            name="General",
        ),
        FieldSet('delivery_site', 'delivery_location', name='Location'),
    )
    nullable_fields = (
        "date",
        "description",
        "receiving_contact",
        "delivery_location",
    )


class InventoryItemTypeImportForm(NetBoxModelImportForm):
    manufacturer = CSVModelChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name="name",
        help_text="Manufacturer. It must exist before import.",
        required=True,
    )
    inventoryitem_group = CSVModelChoiceField(
        queryset=InventoryItemGroup.objects.all(),
        to_field_name="name",
        help_text="Group of inventory item types. It must exist before import.",
        required=False,
    )

    class Meta:
        model = InventoryItemType
        fields = (
            "model",
            "slug",
            "manufacturer",
            "description",
            "part_number",
            "inventoryitem_group",
            "comments",
            "tags",
        )


class InventoryItemTypeBulkEditForm(NetBoxModelBulkEditForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        label="Manufacturer",
    )
    inventoryitem_group = DynamicModelChoiceField(
        queryset=InventoryItemGroup.objects.all(),
        required=False,
        label="Inventory Item Group",
    )
    description = forms.CharField(max_length=200, required=False)
    comments = CommentField(
        required=False,
    )

    model = InventoryItemType
    fieldsets = (
        FieldSet(
            "manufacturer",
            "inventoryitem_group",
            "description",
            name="Inventory Item Type",
        ),
    )
    nullable_fields = ("inventoryitem_group", "description", "comments")


class InventoryItemGroupImportForm(NetBoxModelImportForm):
    parent = CSVModelChoiceField(
        queryset=InventoryItemGroup.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Name of parent group",
    )

    class Meta:
        model = InventoryItemGroup
        fields = ("name", "parent", "description", "comments", "tags")


class InventoryItemGroupBulkEditForm(NetBoxModelBulkEditForm):
    parent = DynamicModelChoiceField(
        queryset=InventoryItemGroup.objects.all(), required=False
    )
    description = forms.CharField(max_length=200, required=False)
    comments = CommentField(
        required=False,
    )

    model = InventoryItemGroup
    fieldsets = (FieldSet("parent", "description"),)
    nullable_fields = (
        "parent",
        "description",
    )


class CourierImportForm(NetBoxModelImportForm):
    class Meta:
        model = Courier
        fields = ('name', 'slug', 'description', 'comments', 'tags')


class CourierBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(
        required=False,
    )
    comments = CommentField(
        required=False,
    )

    model = Courier
    fieldsets = (FieldSet('description', name='General'),)
    nullable_fields = ('description',)


class TransferImportForm(NetBoxModelImportForm):
    courier = CSVModelChoiceField(
        queryset=Courier.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Courier that is handling this transfer.',
    )
    status = CSVChoiceField(
        choices=TransferStatusChoices,
        help_text='Transfer lifecycle status.',
    )
    sender = CSVModelChoiceField(
        queryset=Contact.objects.all(),
        to_field_name='name',
        required=True,
        help_text='Contact that is sending this transfer. It must exist before import.',
    )
    recipient = CSVModelChoiceField(
        queryset=Contact.objects.all(),
        to_field_name='name',
        required=True,
        help_text='Contact that is receiving this transfer. It must exist before import.',
    )
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text='Site where this transfer is to be delivered. It must exist before import.',
        required=True,
    )
    location = CSVModelChoiceField(
        queryset=Location.objects.all(),
        to_field_name='name',
        help_text='On-site location where this transfer is to be delivered. It must exist before import.',
        required=False,
    )
    pickup_date = forms.DateField(
        help_text='Date the courier picked up the transfer from sender.',
        required=False,
    )
    received_date = forms.DateField(
        help_text='Date the courier delivered the transfer to recipient.',
        required=False,
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
            'comments',
            'tags',
        )


class TransferBulkEditForm(NetBoxModelBulkEditForm):
    name = forms.CharField(
        required=False,
    )
    courier = DynamicModelChoiceField(
        queryset=Courier.objects.all(),
        help_text=Transfer._meta.get_field('courier').help_text,
        required=False,
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(TransferStatusChoices),
        required=False,
        initial='',
    )
    sender = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        help_text=Transfer._meta.get_field('sender').help_text,
        required=False,
    )
    recipient = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        help_text=Transfer._meta.get_field('recipient').help_text,
        required=False,
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        help_text=Transfer._meta.get_field('site').help_text,
        required=False,
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        help_text=Transfer._meta.get_field('location').help_text,
        required=False,
    )
    pickup_date = forms.DateField(
        label='Pickup Date', required=False, widget=DatePicker()
    )
    received_date = forms.DateField(
        label='Pickup Date', required=False, widget=DatePicker()
    )
    comments = CommentField(
        required=False,
    )

    model = Transfer
    fieldsets = (
        FieldSet('name', 'courier', 'status', name='General'),
        FieldSet(
            'sender',
            'recipient',
            'site',
            'location',
            'pickup_date',
            'received_date',
            name='Transfer',
        ),
    )
    nullable_fields = (
        'name',
        'courier',
        'recipient',
        'pickup_date',
        'received_date',
    )


class CourierImportForm(NetBoxModelImportForm):
    class Meta:
        model = Courier
        fields = ('name', 'slug', 'description', 'comments', 'tags')


class CourierBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(
        required=False,
    )
    comments = CommentField(
        required=False,
    )

    model = Courier
    fieldsets = (FieldSet('description', name='General'),)
    nullable_fields = ('description',)


class TransferImportForm(NetBoxModelImportForm):
    courier = CSVModelChoiceField(
        queryset=Courier.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Courier that is handling this transfer.',
    )
    status = CSVChoiceField(
        choices=TransferStatusChoices,
        help_text='Transfer lifecycle status.',
    )
    sender = CSVModelChoiceField(
        queryset=Contact.objects.all(),
        to_field_name='name',
        required=True,
        help_text='Contact that is sending this transfer. It must exist before import.',
    )
    recipient = CSVModelChoiceField(
        queryset=Contact.objects.all(),
        to_field_name='name',
        required=True,
        help_text='Contact that is receiving this transfer. It must exist before import.',
    )
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text='Site where this transfer is to be delivered. It must exist before import.',
        required=True,
    )
    location = CSVModelChoiceField(
        queryset=Location.objects.all(),
        to_field_name='name',
        help_text='On-site location where this transfer is to be delivered. It must exist before import.',
        required=False,
    )
    pickup_date = forms.DateField(
        help_text='Date the courier picked up the transfer from sender.',
        required=False,
    )
    received_date = forms.DateField(
        help_text='Date the courier delivered the transfer to recipient.',
        required=False,
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
            'comments',
            'tags',
        )


class TransferBulkEditForm(NetBoxModelBulkEditForm):
    name = forms.CharField(
        required=False,
    )
    courier = DynamicModelChoiceField(
        queryset=Courier.objects.all(),
        help_text=Transfer._meta.get_field('courier').help_text,
        required=False,
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(TransferStatusChoices),
        required=False,
        initial='',
    )
    sender = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        help_text=Transfer._meta.get_field('sender').help_text,
        required=False,
    )
    recipient = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        help_text=Transfer._meta.get_field('recipient').help_text,
        required=False,
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        help_text=Transfer._meta.get_field('site').help_text,
        required=False,
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        help_text=Transfer._meta.get_field('location').help_text,
        required=False,
    )
    pickup_date = forms.DateField(
        label='Pickup Date', required=False, widget=DatePicker()
    )
    received_date = forms.DateField(
        label='Pickup Date', required=False, widget=DatePicker()
    )
    comments = CommentField(
        required=False,
    )

    model = Transfer
    fieldsets = (
        FieldSet('name', 'courier', 'status', name='General'),
        FieldSet(
            'sender',
            'recipient',
            'site',
            'location',
            'pickup_date',
            'received_date',
            name='Transfer',
        ),
    )
    nullable_fields = (
        'name',
        'courier',
        'recipient',
        'pickup_date',
        'received_date',
    )
