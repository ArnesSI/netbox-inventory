from dcim.models import DeviceType, Manufacturer, ModuleType, Location, Site
from netbox.forms import NetBoxModelForm
from netbox_inventory.choices import HardwareKindChoices
from utilities.forms import CommentField, DatePicker, DynamicModelChoiceField, SlugField
from tenancy.models import Tenant
from ..models import Asset, InventoryItemType, InventoryItemGroup, Purchase, Supplier
from ..utils import get_tags_and_edit_protected_asset_fields

__all__ = (
    'AssetForm',
    'SupplierForm',
    'PurchaseForm',
    'InventoryItemTypeForm',
    'InventoryItemGroupForm',
)


class AssetForm(NetBoxModelForm):

    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        initial_params={
            'device_types': '$device_type',
            'module_types': '$module_type',
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
        ('General', ('name', 'asset_tag', 'tags', 'status')),
        (
            'Hardware',
            (
                'serial',
                'manufacturer',
                'device_type',
                'module_type',
                'inventoryitem_type',
            ),
        ),
        (
            'Purchase',
            (
                'owner',
                'purchase',
                'warranty_start',
                'warranty_end',
            ),
        ),
        (
            'Location',
            (
                'storage_site',
                'storage_location',
            ),
        ),
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
            'storage_location',
            'owner',
            'purchase',
            'warranty_start',
            'warranty_end',
            'tags',
            'comments',
            'storage_site',
        )
        widgets = {
            'warranty_start': DatePicker(),
            'warranty_end': DatePicker(),
        }

    def __init__(self, *args, **kwargs):
        """Override the default __init__ method to add custom logic to the form.
        We need to disable fields that are not editable based on the tags that are assigned to the asset.
        """
        super().__init__(*args, **kwargs)

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

        # if assigned to device/module/inventoryitem we can't change device_type/...
        if (
            self.instance.device or self.instance.module
            or self.instance.inventoryitem
        ):
            self.fields['manufacturer'].disabled = True
            for kind in HardwareKindChoices.values():
                self.fields[f'{kind}_type'].disabled = True


class SupplierForm(NetBoxModelForm):
    slug = SlugField(slug_source='name')
    comments = CommentField()

    fieldsets = (('Supplier', ('name', 'slug', 'description', 'tags')),)

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

    fieldsets = (('Purchase', ('supplier', 'name', 'date', 'description', 'tags')),)

    class Meta:
        model = Purchase
        fields = (
            'supplier',
            'name',
            'date',
            'description',
            'comments',
            'tags',
        )
        widgets = {
            'date': DatePicker(),
        }


class InventoryItemTypeForm(NetBoxModelForm):
    slug = SlugField(slug_source='model')
    comments = CommentField()

    fieldsets = (
        (
            'Inventory Item Type',
            ('manufacturer', 'model', 'slug', 'part_number', 'inventoryitem_group', 'tags'),
        ),
    )

    class Meta:
        model = InventoryItemType
        fields = (
            'manufacturer',
            'model',
            'slug',
            'part_number',
            'inventoryitem_group',
            'tags',
            'comments',
        )


class InventoryItemGroupForm(NetBoxModelForm):
    comments = CommentField()

    fieldsets = (
        (
            'Inventory Item Group',
            ('name', 'tags'),
        ),
    )

    class Meta:
        model = InventoryItemGroup
        fields = (
            'name',
            'tags',
            'comments',
        )
