from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify

from dcim.models import DeviceType, Manufacturer, ModuleType, Location, Site
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelCSVForm
from utilities.forms import (
    add_blank_choice, ChoiceField, CommentField, CSVChoiceField,
    CSVModelChoiceField, DynamicModelChoiceField
)
from tenancy.models import Tenant
from ..choices import AssetStatusChoices, HardwareKindChoices
from ..models import Asset, InventoryItemType, InventoryItemGroup, Purchase, Supplier
from ..utils import get_plugin_setting

__all__ = (
    'AssetBulkEditForm',
    'AssetCSVForm',
    'InventoryItemTypeBulkEditForm',
)


class AssetBulkEditForm(NetBoxModelBulkEditForm):
    name = forms.CharField(
        required=False,
    )
    status = ChoiceField(
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
        help_text='What kind of hardware is this.',
    )
    manufacturer = CSVModelChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name='name',
        required=True,
        help_text='Hardware manufacturer.'
    )
    model_name = forms.CharField(
        required=True,
        help_text='Model of this device/module/inventory item type. See "Import settings" below for more info.',
    )
    part_number = forms.CharField(
        required=False,
        help_text='Discrete part number for model. Only used if creating new model.',
    )
    model_comments = forms.CharField(
        required=False,
        help_text='Comments for model. Only used if creating new model.',
    )
    status = CSVChoiceField(
        choices=AssetStatusChoices,
        help_text='Asset lifecycle status.',
    )
    storage_site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        help_text='Site that contains storage_location asset will be stored in.',
        required=False,
    )
    storage_location = CSVModelChoiceField(
        queryset=Location.objects.all(),
        to_field_name='name',
        help_text='Location where is this asset stored when not in use. It must exist before import.',
        required=False,
    )
    owner = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='name',
        help_text='Tenant that owns this asset. It must exist before import.',
        required=False,
    )
    purchase = CSVModelChoiceField(
        queryset=Purchase.objects.all(),
        to_field_name='name',
        help_text='Purchase through which this asset was purchased. See "Import settings" below for more info.',
        required=False,
    )
    purchase_date = forms.DateField(
        help_text='Date when this purchase was made.',
        required=False,
    )
    supplier = CSVModelChoiceField(
        queryset=Supplier.objects.all(),
        to_field_name='name',
        help_text='Legal entity this purchase was made from. Required if a new purchase was given.',
        required=False,
    )

    class Meta:
        model = Asset
        fields = (
            'name', 'asset_tag', 'serial', 'status',
            'hardware_kind', 'manufacturer', 'model_name', 'part_number',
            'model_comments', 'storage_site', 'storage_location',
            'owner', 'purchase', 'purchase_date', 'supplier',
            'warranty_start', 'warranty_end', 'comments',
        )

    def clean_model_name(self):
        hardware_kind = self.cleaned_data.get('hardware_kind')
        manufacturer = self.cleaned_data.get('manufacturer')
        model = self.cleaned_data.get('model_name')
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
            # filter storage_location queryset on selected storage_site
            params = {f"site__{self.fields['storage_site'].to_field_name}": data.get('storage_site')}
            self.fields['storage_location'].queryset = self.fields['storage_location'].queryset.filter(**params)

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
        device_type, module_type or inventory_item dinamically. So we remove those
        fields from exclusions.
        """
        exclude = super()._get_validation_exclusions()
        exclude.remove('device_type')
        exclude.remove('module_type')
        exclude.remove('inventoryitem_type')
        return exclude

    def _create_related_objects(self):
        """
        Create missing related objects (Purchase, DeviceType...). Based on plugin
        settings.
        On exceptions we add to form errors so user gets correct feedback that
        something is wrong. 
        """
        try:
            # handle creating related resources if they don't exist and enabled in settings
            if (get_plugin_setting('asset_import_create_purchase')
                and self.data.get('purchase') and self.data.get('supplier')):
                Purchase.objects.get_or_create(
                    name=self.data.get('purchase'),
                    supplier=self._get_or_create_supplier(),
                    defaults={'date': self._get_clean_value('purchase_date')}
                )
            if (get_plugin_setting('asset_import_create_device_type')
                and self.data.get('hardware_kind') == 'device'):
                DeviceType.objects.get_or_create(
                    model__iexact=self.data.get('model_name'),
                    manufacturer=self._get_or_create_manufacturer(),
                    defaults={
                        'model': self.data.get('model_name'),
                        'slug': slugify(self.data.get('model_name')),
                        'part_number': self._get_clean_value('part_number'),
                        'comments': self._get_clean_value('model_comments'),
                    },
                )
            if (get_plugin_setting('asset_import_create_module_type')
                and self.data.get('hardware_kind') == 'module'):
                ModuleType.objects.get_or_create(
                    model__iexact=self.data.get('model_name'),
                    manufacturer=self._get_or_create_manufacturer(),
                    defaults={
                        'model': self.data.get('model_name'),
                        'part_number': self._get_clean_value('part_number'),
                        'comments': self._get_clean_value('model_comments'),
                    },
                )
            if (get_plugin_setting('asset_import_create_inventoryitem_type')
                and self.data.get('hardware_kind') == 'inventoryitem'):
                InventoryItemType.objects.get_or_create(
                    model__iexact=self.data.get('model_name'),
                    manufacturer=self._get_or_create_manufacturer(),
                    defaults={
                        'model': self.data.get('model_name'),
                        'slug': slugify(self.data.get('model_name')),
                        'part_number': self._get_clean_value('part_number'),
                        'comments': self._get_clean_value('model_comments'),
                    },
                )
        except forms.ValidationError as e:
            # ValidationErrors are raised by _clean_fields() method
            # this will be called later in the code and will be bound
            # to correct field. So we skiup this kinds of errors here.
            pass
        except Exception as e:
            # any other errors we add to non-field specific form errors
            self.add_error(None, e)

    def _get_or_create_manufacturer(self):
        manufacturer, _ = Manufacturer.objects.get_or_create(
            name__iexact=self.data.get('manufacturer'),
            defaults={
                'name': self.data.get('manufacturer'),
                'slug': slugify(self.data.get('manufacturer'))
            },
        )
        return manufacturer

    def _get_or_create_supplier(self):
        supplier, _ = Supplier.objects.get_or_create(
            name__iexact=self.data.get('supplier'),
            defaults={
                'name': self.data.get('supplier'),
                'slug': slugify(self.data.get('supplier'))
            }
        )
        return supplier

    def _get_clean_value(self, field_name):
        """
        Returns cleaned value for a given field from self.data
        Used when creating additional related objects on import, since the values
        are otherwise not validated by forms.
        Used for DateTime, Boolean and similar fields. If used on ModelField and
        instance does not exist it raises Exception but no feedback is given to user.
        """
        try:
            return self.fields[field_name].clean(self.data.get(field_name))
        except forms.ValidationError as e:
            self.add_error(field_name, e)
            raise


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
    comments = CommentField(
        required=False,
    )

    model = InventoryItemType
    fieldsets = (
        ('Inventory Item Type', ('manufacturer', 'inventoryitem_group')),
    )
    nullable_fields = (
        'inventoryitem_group',
    )
