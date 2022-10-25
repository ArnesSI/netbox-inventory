from django import forms
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify

from dcim.models import DeviceType, Manufacturer, ModuleType, Location, Site
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelCSVForm
from utilities.forms import (
    add_blank_choice, ChoiceField, CommentField, CSVChoiceField,
    CSVModelChoiceField, DynamicModelChoiceField
)
from tenancy.models import Tenant
from ..choices import InventoryStatusChoices, HardwareKindChoices
from ..models import Asset, InventoryItemType, Purchase, Supplier

__all__ = (
    'AssetBulkEditForm',
    'AssetCSVForm',
)


class AssetBulkEditForm(NetBoxModelBulkEditForm):
    name = forms.CharField(
        required=False,
    )
    status = ChoiceField(
        choices=add_blank_choice(InventoryStatusChoices),
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
    order_number = forms.CharField(
        required=False,
    )
    # FIXME figure out how to use DateFicker field for these
    purchase_date = forms.CharField(
        required=False,
    )
    warranty_start = forms.CharField(
        required=False,
    )
    warranty_end = forms.CharField(
        required=False,
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
        ('General', ('name', 'status')),
        ('Hardware', ('device_type', 'device', 'module_type', 'module')),
        ('Purchase', ('owner', 'purchase', 'warranty_start', 'warranty_end')), 
        ('Location', ('storage_location',)),
    )
    nullable_fields = (
        'name', 'device', 'module', 'owner', 'purchase', 'warranty_start',
        'warranty_end',
    )


class AssetCSVForm(NetBoxModelCSVForm):
    hardware_kind = CSVChoiceField(
        choices=HardwareKindChoices,
        required=True,
        help_text='What kind of hardware is this',
    )
    manufacturer = CSVModelChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name='name',
        required=True,
        help_text='Hardware manufacturer'
    )
    hardware_type = forms.CharField(
        required=True,
        help_text='Hardware type (model)',
    )
    status = CSVChoiceField(
        choices=InventoryStatusChoices,
        help_text='Asset lifecycle status',
    )
    storage_site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text='Site that contains Location asset is stored in',
        required=False,
    )
    storage_location = CSVModelChoiceField(
        queryset=Location.objects.all(),
        to_field_name='name',
        help_text=Asset._meta.get_field('storage_location').help_text,
        required=not Asset._meta.get_field('storage_location').blank,
    )
    owner = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='name',
        help_text='Tenant that owns this asset',
        required=not Asset._meta.get_field('owner').blank,
    )
    purchase = CSVModelChoiceField(
        queryset=Purchase.objects.all(),
        to_field_name='name',
        help_text=Asset._meta.get_field('purchase').help_text,
        required=not Asset._meta.get_field('purchase').blank,
    )
    purchase_date = forms.CharField(
        help_text='Required if purchase was given',
        required=False,
    )
    supplier = CSVModelChoiceField(
        queryset=Supplier.objects.all(),
        to_field_name='name',
        help_text='Required if purchase was given',
        required=False,
    )

    class Meta:
        model = Asset
        fields = (
            'name', 'asset_tag', 'serial', 'status',
            'hardware_kind', 'manufacturer', 'hardware_type',
            'storage_site', 'storage_location',
            'owner', 'purchase', 'purchase_date', 'supplier',
            'warranty_start', 'warranty_end', 'comments',
        )

    def clean_hardware_type(self):
        hardware_kind = self.cleaned_data.get('hardware_kind')
        manufacturer = self.cleaned_data.get('manufacturer')
        model = self.cleaned_data.get('hardware_type')
        if not hardware_kind or not manufacturer:
            # clean on manufacturer or hardware_kind already raises
            return None
        if hardware_kind == 'device':
            hardware_class = DeviceType
        elif hardware_kind == 'module':
            hardware_class = ModuleType
        elif hardware_kind == 'inventoryitem':
            hardware_class = InventoryItemType
        try:
            hardware_type = hardware_class.objects.get(manufacturer=manufacturer, model=model)
        except ObjectDoesNotExist:
            raise forms.ValidationError(f'Hardware type not found: "{hardware_kind}", "{manufacturer}", "{model}"')
        setattr(self.instance, f'{hardware_kind}_type', hardware_type)
        return hardware_type

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:
            params = {f"site__{self.fields['storage_site'].to_field_name}": data.get('storage_site')}
            self.fields['storage_location'].queryset = self.fields['storage_location'].queryset.filter(**params)

            # handle creating related resources if they don't exist and enabled in settings
            if (settings.PLUGINS_CONFIG['netbox_inventory']['asset_import_create_purchase']
                and data.get('purchase') and data.get('supplier')):
                Purchase.objects.get_or_create(
                    name=data.get('purchase'),
                    supplier=self._get_or_create_supplier(data),
                    defaults={'date': data.get('purchase_date')}
                )
            if (settings.PLUGINS_CONFIG['netbox_inventory']['asset_import_create_device_type']
                and data.get('hardware_kind') == 'device'):
                DeviceType.objects.get_or_create(
                    model=data.get('hardware_type'),
                    manufacturer=self._get_or_create_manufacturer(data),
                    defaults={'slug': slugify(data.get('hardware_type'))},
                )
            if (settings.PLUGINS_CONFIG['netbox_inventory']['asset_import_create_module_type']
                and data.get('hardware_kind') == 'module'):
                ModuleType.objects.get_or_create(
                    model=data.get('hardware_type'),
                    manufacturer=self._get_or_create_manufacturer(data),
                )
            if (settings.PLUGINS_CONFIG['netbox_inventory']['asset_import_create_inventoryitem_type']
                and data.get('hardware_kind') == 'inventoryitem'):
                InventoryItemType.objects.get_or_create(
                    model__iexact=data.get('hardware_type'),
                    manufacturer=self._get_or_create_manufacturer(data),
                    defaults={'slug': slugify(data.get('hardware_type'))},
                )

    def _get_or_create_manufacturer(self, data):
        manufacturer, _ = Manufacturer.objects.get_or_create(
            name__iexact=data.get('manufacturer'),
            defaults={
                'name': data.get('manufacturer'),
                'slug': slugify(data.get('manufacturer'))
            },
        )
        return manufacturer

    def _get_or_create_supplier(self, data):
        supplier, _ = Supplier.objects.get_or_create(
            name__iexact=data.get('supplier'),
            defaults={
                'name': data.get('supplier'),
                'slug': slugify(data.get('supplier'))
            }
        )
        return supplier
