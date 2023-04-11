from django.test import override_settings

from dcim.models import Manufacturer, DeviceType, DeviceRole, Device, InventoryItem, Module, ModuleBay, ModuleType, Site
from utilities.testing import ViewTestCases

from netbox_inventory.tests.custom import ModelViewTestCase
from netbox_inventory.models import Asset, InventoryItemType
from ..settings import CONFIG_SYNC_ON


class AssetCreateHwBase():
    """
    Base class for tests that create hardware and assign Asset to it
    """

    def setUp(self):
        super().setUp()

        self.site1 = Site.objects.create(
            name='site1',
            slug='site1',
            status='active',
        )
        self.manufacturer1 = Manufacturer.objects.create(
            name='manufacturer1',
            slug='manufacturer1',
        )
        self.device_type1 = DeviceType.objects.create(
            manufacturer=self.manufacturer1,
            model='device_type1',
            slug='device_type1'
        )
        self.module_type1 = ModuleType.objects.create(
            manufacturer=self.manufacturer1,
            model='module_type1',
        )
        self.device_role1 = DeviceRole.objects.create(
            name='device_role1',
            slug='device_role1'
        )
        self.inventoryitem_type1 = InventoryItemType.objects.create(
            manufacturer=self.manufacturer1,
            model='inventoryitem_type1',
            slug='inventoryitem_type1'
        )
        self.device1 = Device.objects.create(
            site=self.site1,
            status='active',
            device_type=self.device_type1,
            device_role=self.device_role1,
            name='device1',
        )
        self.module_bay1 = ModuleBay.objects.create(
            device=self.device1,
            name='1',
        )
        self.asset_device_sn = Asset.objects.create(
            asset_tag='asset_device',
            serial='asset_device',
            status='stored',
            device_type=self.device_type1,
        )
        self.asset_module_sn = Asset.objects.create(
            asset_tag='asset_module',
            serial='asset_module',
            status='stored',
            module_type=self.module_type1,
        )
        self.asset_inventoryitem_sn = Asset.objects.create(
            asset_tag='asset_inventoryitem',
            serial='asset_inventoryitem',
            status='stored',
            inventoryitem_type=self.inventoryitem_type1,
        )
        self.asset_device_no = Asset.objects.create(
            status='stored',
            device_type=self.device_type1,
        )
        self.asset_module_no = Asset.objects.create(
            status='stored',
            module_type=self.module_type1,
        )
        self.asset_inventoryitem_no = Asset.objects.create(
            status='stored',
            inventoryitem_type=self.inventoryitem_type1,
        )

    def _get_url(self, _):
        hardware_kind = self.tested_asset.kind
        if hardware_kind == 'inventoryitem':
            hardware_kind = 'inventory-item'
        return f'/plugins/inventory/assets/{hardware_kind}/create/?asset_id={self.tested_asset.pk}'

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    @override_settings(PLUGINS_CONFIG=CONFIG_SYNC_ON)
    def test_create_object_with_permission(self):
        super().test_create_object_with_permission()
        # in addition to a new inventoryitem instance in db,
        # it must have matching serial and asset2 must have it assigned
        # blank value for Asset.serial is None, but for Device/Module/IItem.serial it's ''
        checked_serial = self.tested_asset.serial or '' 
        instance = self._get_queryset().order_by('pk').last()
        self.assertEqual(instance.asset_tag, self.tested_asset.asset_tag)
        self.assertEqual(instance.serial, checked_serial)
        self.tested_asset.refresh_from_db()
        self.assertEqual(instance, self.tested_asset.hardware)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    @override_settings(PLUGINS_CONFIG=CONFIG_SYNC_ON)
    def test_create_object_with_constrained_permission(self):
        super().test_create_object_with_constrained_permission()
        # in addition to a new inventoryitem instance in db,
        # it must have matching serial and asset2 must have it assigned
        # blank value for Asset.serial is None, but for Device/Module/IItem.serial it's ''
        checked_serial = self.tested_asset.serial or '' 
        instance = self._get_queryset().order_by('pk').last()
        self.assertEqual(instance.asset_tag, self.tested_asset.asset_tag)
        self.assertEqual(instance.serial, checked_serial)
        self.tested_asset.refresh_from_db()
        self.assertEqual(instance, self.tested_asset.hardware)


class SerialDeviceAssetCreateHwTestCase(AssetCreateHwBase, ModelViewTestCase, ViewTestCases.CreateObjectViewTestCase):
    """
    Test creating new Device from Asset with serial
    """
    model = Device

    def setUp(self):
        super().setUp()
        self.form_data = {
            'site': self.site1.pk,
            'device_type': self.device_type1.pk,
            'device_role': self.device_role1.pk,
            'status': 'active',
            'name': 'tested_device',
        }
        self.tested_asset = self.asset_device_sn


class SerialModuleAssetCreateHwTestCase(AssetCreateHwBase, ModelViewTestCase, ViewTestCases.CreateObjectViewTestCase):
    """
    Test creating new Module from Asset with serial
    """
    model = Module

    def setUp(self):
        super().setUp()
        self.form_data = {
            'device': self.device1.pk,
            'module_bay': self.module_bay1.pk,
            'module_type': self.module_type1.pk,
            'status': 'active',
        }
        self.tested_asset = self.asset_module_sn


class SerialInventoryItemAssetCreateHwTestCase(AssetCreateHwBase, ModelViewTestCase, ViewTestCases.CreateObjectViewTestCase):
    """
    Test creating new InventoryItem from Asset with serial
    """
    model = InventoryItem

    def setUp(self):
        super().setUp()
        self.form_data = {
            'device': self.device1.pk,
            'name': 'inventoryitem1',
        }
        self.tested_asset = self.asset_inventoryitem_sn


class NoSerialDeviceAssetCreateHwTestCase(AssetCreateHwBase, ModelViewTestCase, ViewTestCases.CreateObjectViewTestCase):
    """
    Test creating new Device from Asset with blank serial
    """
    model = Device

    def setUp(self):
        super().setUp()
        self.form_data = {
            'site': self.site1.pk,
            'device_type': self.device_type1.pk,
            'device_role': self.device_role1.pk,
            'status': 'active',
            'name': 'tested_device',
        }
        self.tested_asset = self.asset_device_no


class NoSerialModuleAssetCreateHwTestCase(AssetCreateHwBase, ModelViewTestCase, ViewTestCases.CreateObjectViewTestCase):
    """
    Test creating new Module from Asset with blank serial
    """
    model = Module

    def setUp(self):
        super().setUp()
        self.form_data = {
            'device': self.device1.pk,
            'module_bay': self.module_bay1.pk,
            'module_type': self.module_type1.pk,
            'status': 'active',
        }
        self.tested_asset = self.asset_module_no


class NoSerialInventoryItemAssetCreateHwTestCase(AssetCreateHwBase, ModelViewTestCase, ViewTestCases.CreateObjectViewTestCase):
    """
    Test creating new InventoryItem from Asset with blank serial
    """
    model = InventoryItem

    def setUp(self):
        super().setUp()
        self.form_data = {
            'device': self.device1.pk,
            'name': 'inventoryitem1',
        }
        self.tested_asset = self.asset_inventoryitem_no
