from datetime import date

from django.conf import settings
from django.db import models
from django.forms import ValidationError
from django.urls import reverse

from netbox.models import NetBoxModel
from .choices import HardwareKindChoices, InventoryStatusChoices
from .utils import get_prechange_field, get_status_for


class Asset(NetBoxModel):
    """
    An Asset represents a piece of hardware we want to keep track of. It has a
    make (model, part number) that is one of: Device Type, Module Type or
    InventoryItem Type.

    Asset must have a serial number, can have an asset tag (inventory number). It
    must have one of DeviceType, ModuleType or InventoryItemType. It can have a
    storage location (instance of Location). There are also fields to keep track of
    purchase and warranty info.

    An asset that is in use, can be assigned to a Device, Module or InventoryItem.
    """
    #
    # fields that identify asset
    #
    name = models.CharField(
        help_text='Can be used to quickly identify a particular asset',
        max_length=128,
        blank=True,
        null=False,
        default='',
    )
    asset_tag = models.CharField(
        help_text='Identifier assigned by owner',
        max_length=50,
        blank=True,
        null=True,
        default=None,
    )
    serial = models.CharField(
        help_text='Identifier assigned by manufacturer',
        max_length=60,
        verbose_name='Serial number',
        blank=True,
        null=True,
        default=None,
    )

    #
    # status fields
    #
    status = models.CharField(
        max_length=30,
        choices=InventoryStatusChoices,
        help_text='Asset lifecycle status',
    )

    #
    # hardware type fields
    #
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True,
    )
    module_type = models.ForeignKey(
        to='dcim.ModuleType',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True,
    )
    inventoryitem_type = models.ForeignKey(
        to='netbox_inventory.InventoryItemType',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True,
    )

    #
    # used fields
    #
    device = models.OneToOneField(
        to='dcim.Device',
        on_delete=models.SET_NULL,
        related_name='assigned_asset',
        blank=True,
        null=True,
    )
    module = models.OneToOneField(
        to='dcim.Module',
        on_delete=models.SET_NULL,
        related_name='assigned_asset',
        blank=True,
        null=True,
    )
    inventoryitem = models.OneToOneField(
        to='dcim.InventoryItem',
        on_delete=models.SET_NULL,
        related_name='assigned_asset',
        blank=True,
        null=True,
    )
    tenant = models.ForeignKey(
        help_text='Tenant using this asset',
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True,
    )
    contact = models.ForeignKey(
        help_text='Contact using this asset',
        to='tenancy.Contact',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True,
    )

    storage_location = models.ForeignKey(
        help_text='Where is this asset stored when not in use',
        to='dcim.Location',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True,
    )

    #
    # purchase info
    #
    owner = models.ForeignKey(
        help_text='Who owns this asset',
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True,
    )
    purchase = models.ForeignKey(
        help_text='Purchase through which this asset was purchased',
        to='netbox_inventory.Purchase',
        on_delete=models.PROTECT,
        related_name='assets',
        blank=True,
        null=True,
    )
    warranty_start = models.DateField(
        help_text='First date warranty for this asset is valid',
        blank=True,
        null=True,
    )
    warranty_end = models.DateField(
        help_text='Last date warranty for this asset is valid',
        blank=True,
        null=True,
    )

    comments = models.TextField(
        blank=True
    )

    clone_fields = [
        'status', 'device_type', 'module_type', 'inventoryitem_type', 'tenant', 'contact',
        'storage_location', 'owner', 'purchase', 'warranty_start', 'warranty_end', 'comments'
    ]

    @property
    def kind(self):
        if self.device_type_id:
            return 'device'
        elif self.module_type_id:
            return 'module'
        elif self.inventoryitem_type_id:
            return 'inventoryitem'
        assert False, f'Invalid hardware kind detected for asset {self.pk}'

    def get_kind_display(self):
        return dict(HardwareKindChoices)[self.kind]

    @property
    def hardware_type(self):
        return self.device_type or self.module_type or self.inventoryitem_type or None

    @property
    def hardware(self):
        return self.device or self.module or self.inventoryitem or None

    @property
    def warranty_remaining(self):
        """
            How many days are left in warranty period.
            Returns negative duration if period has not started yet
            Return None if warranty_end not defined
        """
        if self.warranty_end:
            if self.warranty_start and self.warranty_start > date.today():
                return date.today() - self.warranty_start
            else:
                return self.warranty_end - date.today()
        return None

    @property
    def warranty_elapsed(self):
        """
            How many days have passed in warranty period.
            Returns negative duration if period has not started yet
            Return None if warranty_start not defined
        """
        if self.warranty_start:
            return date.today() - self.warranty_start
        return None

    @property
    def warranty_total(self):
        if self.warranty_end and self.warranty_start:
            return self.warranty_end - self.warranty_start
        return None

    def clean(self):
        self.validate_hardware_types()
        self.validate_hardware()
        self.update_status()
        return super().clean()

    def save(self, *args, **kwargs):
        self.update_hardware_used()
        return super().save(*args, **kwargs)

    def validate_hardware_types(self):
        """Ensure only one device/module_type/inventoryitem_type is set at a time."""
        if sum(map(bool, [self.device_type, self.module_type, self.inventoryitem_type])) > 1:
            raise ValidationError('Only one of device type, module type and inventory item type can be set for the same asset.')
        if not self.device_type and not self.module_type and not self.inventoryitem_type:
            raise ValidationError('One of device type, module type or inventory item type must be set.')

    def validate_hardware(self):
        """Ensure only one device/module is set at a time and it matches device/module_type."""
        kind = self.kind
        _type = getattr(self, kind+'_type')
        hw = getattr(self, kind)
        hw_others = dict(HardwareKindChoices).keys() - [kind]

        # e.g.: self.device_type and self.device.device_type must match
        # InventoryItem does not have FK to InventoryItemType
        if kind != 'inventoryitem' and hw and _type != getattr(hw, kind+'_type'):
            raise ValidationError({kind: f'{kind} type of {kind} does not match {kind} type of asset'})
        # ensure only one hardware is set and that it is correct kind
        # e.g. if self.device_type is set, we cannot have self.module or self.inventoryitem set
        for hw_other in hw_others:
            if getattr(self, hw_other):
                raise ValidationError(f'Cannot set {hw_other} for asset that is a {kind}')

    def update_status(self):
        """ If asset was assigned or unassigned to a particular device, module, inventoryitem
            update asset.status. Depending on plugin configuration.
        """
        old_hw = get_prechange_field(self, self.kind)
        new_hw = getattr(self, self.kind)
        old_status = get_prechange_field(self, 'status')
        stored_status = get_status_for('stored')
        used_status = get_status_for('used')
        if old_status != self.status:
            # status has also been changed manually, don't change it automatically
            return
        if used_status and new_hw and not old_hw:
            self.status = used_status
        elif stored_status and not new_hw and old_hw:
            self.status = stored_status

    def update_hardware_used(self):
        """ If assigning as device, module or inventoryitem set serial and
            asset_tag on it. Also remove them if unasigning.
        """
        if not settings.PLUGINS_CONFIG['netbox_inventory']['sync_hardware_serial_asset_tag']:
            return None
        old_hw = get_prechange_field(self, self.kind)
        new_hw = getattr(self, self.kind)
        old_serial = get_prechange_field(self, 'serial')
        old_asset_tag = get_prechange_field(self, 'asset_tag')
        # device, module... needs None for unset asset_tag to enforce uniqness at DB level
        new_asset_tag = self.asset_tag if self.asset_tag else None
        # device, module... does not allow serial to be null
        new_serial = self.serial if self.serial else ''
        if not new_hw and old_hw:
            old_hw.serial = ''
            old_hw.asset_tag = None
            old_hw.save()
        elif new_hw and old_hw != new_hw:
            # assigned something, set its serial
            if old_hw:
                # but first clear previous hw data
                old_hw.serial = ''
                old_hw.asset_tag = None
                old_hw.save()
            # if new_hw already has correct values, don't save it again
            new_hw_save = False
            if new_hw.serial != new_serial:
                new_hw.serial = new_serial
                new_hw_save = True
            if new_hw.asset_tag != new_asset_tag:
                new_hw.asset_tag = new_asset_tag
                new_hw_save = True
            if new_hw_save:
                new_hw.save()
        elif self.serial != old_serial or self.asset_tag != old_asset_tag:
            # just changed asset's serial or asset_tag, update assigned hw
            if new_hw:
                new_hw.serial = new_serial
                new_hw.asset_tag = new_asset_tag
                new_hw.save()

    def get_absolute_url(self):
        return reverse('plugins:netbox_inventory:asset', args=[self.pk])
    
    def get_status_color(self):
        return InventoryStatusChoices.colors.get(self.status)

    def __str__(self):
        return f'{self.hardware_type} {self.serial}'

    class Meta:
        ordering = ('device_type', 'module_type', 'inventoryitem_type', 'serial',)
        unique_together = (
            ('device_type', 'serial'),
            ('module_type', 'serial'),
            ('inventoryitem_type', 'serial'),
            ('owner', 'asset_tag'),
        )


class Supplier(NetBoxModel):
    """
    Supplier is a legal entity that sold some assets that we keep track of.
    This can be the same entity as Manufacturer or a separate one. However
    netbox_inventory keeps track of Suppliers separate from Manufacturers.
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    comments = models.TextField(
        blank=True
    )

    clone_fields = [
        'description', 'comments'
    ]

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_inventory:supplier', args=[self.pk])


class Purchase(NetBoxModel):
    """
    Represents a purchase of a set of Assets from a Supplier.
    """
    name = models.CharField(
        max_length=100
    )
    supplier = models.ForeignKey(
        help_text='Legal entity this purchase was made at',
        to='netbox_inventory.Supplier',
        on_delete=models.PROTECT,
        related_name='purchases',
        blank=False,
        null=False,
    )
    date = models.DateField(
        help_text='Date when this purchase was made',
        blank=True,
        null=True,
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    comments = models.TextField(
        blank=True
    )

    clone_fields = [
        'supplier', 'date', 'description', 'comments'
    ]

    class Meta:
        ordering = ['supplier', 'name']
        unique_together = (
            ('supplier', 'name'),
        )

    def __str__(self):
        return f'{self.supplier} {self.name}'

    def get_absolute_url(self):
        return reverse('plugins:netbox_inventory:purchase', args=[self.pk])


class InventoryItemType(NetBoxModel):
    """
    Inventory Item Type is a model (make, part number) of an Inventory Item. In
    that it is simmilar to Device Type or Module Type.
    """
    manufacturer = models.ForeignKey(
        to='dcim.Manufacturer',
        on_delete=models.PROTECT,
        related_name='inventoryitem_types'
    )
    model = models.CharField(
        max_length=100
    )
    slug = models.SlugField(
        max_length=100
    )
    part_number = models.CharField(
        max_length=50,
        blank=True,
        help_text='Discrete part number (optional)'
    )
    comments = models.TextField(
        blank=True
    )

    clone_fields = [
        'manufacturer',
    ]

    class Meta:
        ordering = ['manufacturer', 'model']
        unique_together = [
            ['manufacturer', 'model'],
            ['manufacturer', 'slug'],
        ]

    def __str__(self):
        return self.model

    def get_absolute_url(self):
        return reverse('plugins:netbox_inventory:inventoryitemtype', args=[self.pk])
