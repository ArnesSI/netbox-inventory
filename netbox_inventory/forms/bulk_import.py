from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from core.models import ObjectType
from dcim.models import DeviceType, Location, Manufacturer, ModuleType, RackType, Site
from netbox.forms import NetBoxModelImportForm, PrimaryModelImportForm
from tenancy.models import Contact, Tenant
from utilities.forms.fields import (
    CSVChoiceField,
    CSVContentTypeField,
    CSVModelChoiceField,
)

from ..choices import AssetStatusChoices, HardwareKindChoices, PurchaseStatusChoices
from ..constants import AUDITFLOW_OBJECT_TYPE_CHOICES
from ..models import *
from ..utils import get_plugin_setting

__all__ = (
    'AssetImportForm',
    'AuditFlowImportForm',
    'AuditFlowPageImportForm',
    'AuditTrailImportForm',
    'AuditTrailSourceImportForm',
    'DeliveryImportForm',
    'InventoryItemGroupImportForm',
    'PurchaseImportForm',
    'SupplierImportForm',
    'InventoryItemTypeImportForm',
)


#
# Assets
#


class InventoryItemGroupImportForm(PrimaryModelImportForm):
    parent = CSVModelChoiceField(
        queryset=InventoryItemGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of parent group',
    )

    class Meta:
        model = InventoryItemGroup
        fields = ('name', 'parent', 'description', 'owner', 'comments', 'tags')


class InventoryItemTypeImportForm(PrimaryModelImportForm):
    manufacturer = CSVModelChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name='name',
        help_text='Manufacturer. It must exist before import.',
        required=True,
    )
    inventoryitem_group = CSVModelChoiceField(
        queryset=InventoryItemGroup.objects.all(),
        to_field_name='name',
        help_text='Group of inventory item types. It must exist before import.',
        required=False,
    )

    class Meta:
        model = InventoryItemType
        fields = (
            'model',
            'slug',
            'manufacturer',
            'description',
            'part_number',
            'inventoryitem_group',
            'owner',
            'comments',
            'tags',
        )


class AssetImportForm(PrimaryModelImportForm):
    hardware_kind = CSVChoiceField(
        choices=HardwareKindChoices,
        required=True,
        help_text='What kind of hardware is this.',
    )
    manufacturer = CSVModelChoiceField(
        queryset=Manufacturer.objects.all(),
        to_field_name='name',
        required=True,
        help_text='Hardware manufacturer.',
    )
    model_name = forms.CharField(
        required=True,
        help_text='Model of this device/module/inventory item/rack type. See "Import settings" for more info.',
    )
    part_number = forms.CharField(
        required=False,
        help_text='Discrete part number for model. Only used if creating new model.',
    )
    model_description = forms.CharField(
        required=False,
        help_text='Description for model. Only used if creating new model.',
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
    owning_tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='name',
        help_text='Tenant that owns this asset. It must exist before import.',
        required=False,
    )
    delivery = forms.CharField(
        help_text='Delivery that delivered this asset. See "Import settings" for more info.',
        required=False,
    )
    delivery_date = forms.DateField(
        help_text='Date when this delivery was made.',
        required=False,
    )
    receiving_contact = CSVModelChoiceField(
        queryset=Contact.objects.all(),
        to_field_name='name',
        help_text='Contact that accepted this delivery. It must exist before import.',
        required=False,
    )
    purchase = forms.CharField(
        help_text='Purchase through which this asset was purchased. See "Import settings" for more info.',
        required=False,
    )
    purchase_date = forms.DateField(
        help_text='Date when this purchase was made.',
        required=False,
    )
    purchase_status = CSVChoiceField(
        choices=PurchaseStatusChoices, help_text='Status of purchase', required=False
    )
    supplier = CSVModelChoiceField(
        queryset=Supplier.objects.all(),
        to_field_name='name',
        help_text='Legal entity this purchase was made from. Required if a new purchase is given.',
        required=False,
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='name',
        help_text='Tenant using this asset. See "Import settings" for more info.',
        required=False,
    )
    contact = CSVModelChoiceField(
        queryset=Contact.objects.all(),
        to_field_name='name',
        help_text='Contact using this asset. It must exist before import.',
        required=False,
    )

    class Meta:
        model = Asset
        fields = (
            'name',
            'asset_tag',
            'serial',
            'status',
            'description',
            'hardware_kind',
            'manufacturer',
            'model_name',
            'part_number',
            'model_description',
            'model_comments',
            'storage_site',
            'storage_location',
            'owning_tenant',
            'supplier',
            'purchase',
            'purchase_date',
            'purchase_status',
            'delivery',
            'delivery_date',
            'receiving_contact',
            'warranty_start',
            'warranty_end',
            'owner',
            'comments',
            'tenant',
            'contact',
            'tags',
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
        elif hardware_kind == 'rack':
            hardware_class = RackType
        try:
            hardware_type = hardware_class.objects.get(
                manufacturer=manufacturer, model=model
            )
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                f'Hardware type not found: "{hardware_kind}", "{manufacturer}", "{model}"'
            )
        setattr(self.instance, f'{hardware_kind}_type', hardware_type)
        return hardware_type

    def clean_purchase(self):
        supplier = self.cleaned_data.get('supplier')
        purchase_name = self.cleaned_data.get('purchase')
        if not purchase_name:
            return None
        try:
            purchase = Purchase.objects.get(supplier=supplier, name=purchase_name)
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                f'Unable to find purchase {supplier} {purchase_name}'
            )
        return purchase

    def clean_delivery(self):
        purchase = self.cleaned_data.get('purchase')
        delivery_name = self.cleaned_data.get('delivery')
        if not delivery_name:
            return None
        try:
            delivery = Delivery.objects.get(purchase=purchase, name=delivery_name)
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                f'Unable to find delivery {purchase} {delivery_name}'
            )
        return delivery

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:
            # filter storage_location queryset on selected storage_site
            params = {
                f'site__{self.fields["storage_site"].to_field_name}': data.get(
                    'storage_site'
                )
            }
            self.fields['storage_location'].queryset = self.fields[
                'storage_location'
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
        exclude.remove('device_type')
        exclude.remove('module_type')
        exclude.remove('inventoryitem_type')
        exclude.remove('rack_type')
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
                get_plugin_setting('asset_import_create_purchase')
                and self.data.get('purchase')
                and self.data.get('supplier')
            ):
                purchase, _ = Purchase.objects.get_or_create(
                    name=self.data.get('purchase'),
                    supplier=self._get_or_create_related('supplier'),
                    defaults={
                        'date': self._get_clean_value('purchase_date'),
                        'status': self._get_clean_value('purchase_status'),
                    },
                )
                if self.data.get('delivery'):
                    Delivery.objects.get_or_create(
                        name=self.data.get('delivery'),
                        purchase=purchase,
                        defaults={
                            'date': self._get_clean_value('delivery_date'),
                            'receiving_contact': self._get_clean_value(
                                'receiving_contact'
                            ),
                        },
                    )
            if (
                get_plugin_setting('asset_import_create_device_type')
                and self.data.get('hardware_kind') == 'device'
            ):
                DeviceType.objects.get_or_create(
                    model__iexact=self.data.get('model_name'),
                    manufacturer=self._get_or_create_related('manufacturer'),
                    defaults={
                        'model': self.data.get('model_name'),
                        'slug': slugify(self.data.get('model_name')),
                        'part_number': self._get_clean_value('part_number'),
                        'description': self._get_clean_value('model_description'),
                        'comments': self._get_clean_value('model_comments'),
                    },
                )
            if (
                get_plugin_setting('asset_import_create_module_type')
                and self.data.get('hardware_kind') == 'module'
            ):
                ModuleType.objects.get_or_create(
                    model__iexact=self.data.get('model_name'),
                    manufacturer=self._get_or_create_related('manufacturer'),
                    defaults={
                        'model': self.data.get('model_name'),
                        'part_number': self._get_clean_value('part_number'),
                        'description': self._get_clean_value('model_description'),
                        'comments': self._get_clean_value('model_comments'),
                    },
                )
            if (
                get_plugin_setting('asset_import_create_inventoryitem_type')
                and self.data.get('hardware_kind') == 'inventoryitem'
            ):
                InventoryItemType.objects.get_or_create(
                    model__iexact=self.data.get('model_name'),
                    manufacturer=self._get_or_create_related('manufacturer'),
                    defaults={
                        'model': self.data.get('model_name'),
                        'slug': slugify(self.data.get('model_name')),
                        'part_number': self._get_clean_value('part_number'),
                        'description': self._get_clean_value('model_description'),
                        'comments': self._get_clean_value('model_comments'),
                    },
                )
            if (
                get_plugin_setting('asset_import_create_rack_type')
                and self.data.get('hardware_kind') == 'rack'
            ):
                RackType.objects.get_or_create(
                    model__iexact=self.data.get('model_name'),
                    manufacturer=self._get_or_create_related('manufacturer'),
                    defaults={
                        'model': self.data.get('model_name'),
                        'slug': slugify(self.data.get('model_name')),
                        'description': self._get_clean_value('model_description'),
                        'comments': self._get_clean_value('model_comments'),
                    },
                )
            if get_plugin_setting('asset_import_create_tenant') and self.data.get(
                'tenant'
            ):
                self._get_or_create_related('tenant')
            if get_plugin_setting('asset_import_create_tenant') and self.data.get(
                'owning_tenant'
            ):
                self._get_or_create_related('owning_tenant')
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
            'name': self.data.get(field_name),
            'slug': slugify(self.data.get(field_name)),
        }
        # whatever field was in import data is used as is
        instance_defaults.update({to_field_name: self.data.get(field_name)})
        instance, _ = klass.objects.get_or_create(
            # filter on field specified in column header
            **{to_field_name + '__iexact': self.data.get(field_name)},
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


#
# Deliveries
#


class SupplierImportForm(PrimaryModelImportForm):
    class Meta:
        model = Supplier
        fields = ('name', 'slug', 'description', 'owner', 'comments', 'tags')


class PurchaseImportForm(PrimaryModelImportForm):
    supplier = CSVModelChoiceField(
        queryset=Supplier.objects.all(),
        to_field_name='name',
        help_text='Legal entity this purchase was made at. It must exist when importing.',
        required=True,
    )
    status = CSVChoiceField(
        choices=PurchaseStatusChoices,
        help_text='Status of purchase',
    )

    class Meta:
        model = Purchase
        fields = (
            'name',
            'date',
            'status',
            'supplier',
            'description',
            'owner',
            'comments',
            'tags',
        )


class DeliveryImportForm(PrimaryModelImportForm):
    purchase = CSVModelChoiceField(
        queryset=Purchase.objects.all(),
        to_field_name='id',
        help_text='Purchase that this delivery is part of. It must exist when importing.',
        required=True,
    )
    receiving_contact = CSVModelChoiceField(
        queryset=Contact.objects.all(),
        to_field_name='id',
        help_text='Contact that accepted this delivery. It must exist when importing.',
        required=False,
    )

    class Meta:
        model = Delivery
        fields = (
            'name',
            'date',
            'purchase',
            'receiving_contact',
            'description',
            'owner',
            'comments',
            'tags',
        )


#
# Audit
#


class BaseFlowImportForm(PrimaryModelImportForm):
    """
    Internal base bulk import class for audit flow models.
    """

    object_type = CSVContentTypeField(
        queryset=ObjectType.objects.public(),
        help_text=_('Object Type'),
    )

    class Meta:
        fields = (
            'name',
            'description',
            'owner',
            'tags',
            'object_type',
            'object_filter',
            'comments',
        )


class AuditFlowPageImportForm(BaseFlowImportForm):
    class Meta(BaseFlowImportForm.Meta):
        model = AuditFlowPage


class AuditFlowImportForm(BaseFlowImportForm):
    # Restrict inherited object_type to those object types that represent physical
    # locations.
    object_type = CSVContentTypeField(
        queryset=ObjectType.objects.public(),
        limit_choices_to=AUDITFLOW_OBJECT_TYPE_CHOICES,
        help_text=_('Object Type'),
    )

    class Meta(BaseFlowImportForm.Meta):
        model = AuditFlow
        fields = BaseFlowImportForm.Meta.fields + ('enabled',)


class AuditTrailSourceImportForm(PrimaryModelImportForm):
    class Meta:
        model = AuditTrailSource
        fields = (
            'name',
            'slug',
            'description',
            'owner',
            'tags',
            'comments',
        )


class AuditTrailImportForm(NetBoxModelImportForm):
    object_type = CSVContentTypeField(
        queryset=ObjectType.objects.public(),
        help_text=_('Object Type'),
    )
    source = CSVModelChoiceField(
        queryset=AuditTrailSource.objects.all(),
        to_field_name='slug',
        required=False,
        help_text=_('Source slug of this audit trail.'),
    )

    class Meta:
        model = AuditTrail
        fields = (
            'object_type',
            'object_id',
            'source',
        )
