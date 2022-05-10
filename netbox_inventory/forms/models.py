from dcim.models import DeviceType, Manufacturer, ModuleType, Location, Site
from netbox.forms import NetBoxModelForm
from utilities.forms import CommentField, DatePicker, DynamicModelChoiceField, SlugField
from tenancy.models import Tenant
from ..models import Asset, InventoryItemType, Supplier

__all__ = (
    'AssetForm',
    'SupplierForm',
    'InventoryItemTypeForm',
)

class AssetForm(NetBoxModelForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False,
        initial_params={
            'device_types': '$device_type',
            'module_types': '$module_type',
        }
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
        label='Inventory item type'
    )
    owner = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        help_text=Asset._meta.get_field('owner').help_text,
        required=not Asset._meta.get_field('owner').blank,
    )
    supplier = DynamicModelChoiceField(
        queryset=Supplier.objects.all(),
        help_text=Asset._meta.get_field('supplier').help_text,
        required=not Asset._meta.get_field('supplier').blank,
    )
    storage_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        initial_params={
            'locations': '$storage_location',
        }
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
        ('General', ('name', 'asset_tag', 'status')),
        ('Hardware', ('serial', 'manufacturer', 'device_type', 'module_type', 'inventoryitem_type')),
        ('Purchase', ('owner', 'supplier', 'order_number', 'purchase_date', 'warranty_start', 'warranty_end')),
        ('Location', ('storage_site', 'storage_location',)),
    )

    class Meta:
        model = Asset
        fields = (
            'name', 'asset_tag', 'serial', 'status', 'manufacturer',
            'device_type', 'module_type', 'inventoryitem_type', 'storage_location',
            'owner', 'supplier', 'order_number', 'purchase_date', 'warranty_start',
            'warranty_end', 'tags', 'comments', 'storage_site',
        )
        widgets = {
            'purchase_date': DatePicker(),
            'warranty_start': DatePicker(),
            'warranty_end': DatePicker(),
        }


class SupplierForm(NetBoxModelForm):
    slug = SlugField()
    comments = CommentField()

    fieldsets = (
        ('Supplier', ('name', 'description', 'tags')),
    )

    class Meta:
        model = Supplier
        fields = (
            'name', 'description', 'comments', 'tags',
        )


class InventoryItemTypeForm(NetBoxModelForm):
    slug = SlugField(slug_source='model')
    comments = CommentField()

    fieldsets = (
        ('Inventory Item Type', ('manufacturer', 'model', 'slug', 'part_number', 'tags')),
    )

    class Meta:
        model = InventoryItemType
        fields = (
            'manufacturer', 'model', 'slug', 'part_number', 'tags', 'comments',
        )
