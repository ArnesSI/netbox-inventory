from copy import deepcopy
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings

from dcim.models import Manufacturer, DeviceType, DeviceRole, Device, InventoryItem, Module, ModuleBay, ModuleType, Site
from users.models import ObjectPermission
from utilities.testing import post_data, ViewTestCases

from netbox_inventory.tests.custom import ModelViewTestCase
from netbox_inventory.models import Asset, InventoryItemType


CONFIG_ALLOW_CREATE_DEVICE_TYPE = deepcopy(settings.PLUGINS_CONFIG)
CONFIG_ALLOW_CREATE_DEVICE_TYPE['netbox_inventory']['asset_import_create_device_type']=True


class AssetTestCase(
    ModelViewTestCase,
    ViewTestCases.PrimaryObjectViewTestCase,
):

    model = Asset

    @classmethod
    def setUpTestData(cls):
        site1 = Site.objects.create(
            name='site1',
            slug='site1',
            status='active',
        )
        manufacturer1 = Manufacturer.objects.create(
            name='manufacturer1',
            slug='manufacturer1',
        )
        device_type1 = DeviceType.objects.create(
            model='device_type1',
            slug='device_type1',
            manufacturer=manufacturer1,
            u_height=1,
        )
        device_role1 = DeviceRole.objects.create(
            name='device_role1',
            slug='device_role1',
            color='9e9e9e',
        )
        asset1 = Asset.objects.create(
            status='stored',
            serial='123',
            device_type=device_type1,
        )
        asset2 = Asset.objects.create(
            status='stored',
            serial='223',
            device_type=device_type1,
        )
        asset3 = Asset.objects.create(
            status='stored',
            serial='323',
            device_type=device_type1,
        )

        cls.form_data = {
            'status': 'stored',
            'serial': '124',
            'device_type': device_type1.pk,
        }
        cls.csv_data = (
            'serial,status,hardware_kind,manufacturer,model_name',
            'csv1,stored,device,manufacturer1,device_type1',
            'csv2,stored,device,manufacturer1,device_type1',
            'csv3,stored,device,manufacturer_csv,device_type_csv',
        )
        cls.csv_update_data = (
            'id,serial,status',
            f'{asset1.pk},133,stored',
            f'{asset2.pk},233,stored',
            f'{asset3.pk},333,stored',
        )
        cls.bulk_edit_data = {
            'status': 'retired',
        }

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_create_devcie_from_asset(self):

        # Assign unconstrained permission
        obj_perm = ObjectPermission(
            name='test-device-create permission',
            actions=['add', 'change']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))
        obj_perm.object_types.add(ContentType.objects.get_for_model(Device))

        asset = Asset.objects.create(
            status='stored',
            serial='123create',
            device_type=DeviceType.objects.first(),
        )

        form_data = {
            'name': 'test-device-create',
            'device_role': DeviceRole.objects.first(),
            'device_type': asset.device_type.pk,
            'serial': asset.serial,
            'site': Site.objects.first(),
            'status': 'active',
        }

        request = {
            'path': self._get_url('device_create')+f'?asset_id={asset.pk}',
            'data': post_data(form_data),
        }
        self.assertHttpStatus(self.client.post(**request), 302)

        devices = Device.objects.filter(name=form_data['name'])
        self.assertEqual(len(devices), 1)
        self.assertEqual(devices.first().assigned_asset, asset)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_assign_devcie_from_asset(self):

        # Assign unconstrained permission
        obj_perm = ObjectPermission(
            name='test-device-assign permission',
            actions=['add', 'change']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))
        obj_perm.object_types.add(ContentType.objects.get_for_model(Device))

        asset = Asset.objects.create(
            status='stored',
            serial='123assign',
            device_type=DeviceType.objects.first(),
        )
        device = Device.objects.create(
            name='test-device-assign',
            device_role = DeviceRole.objects.first(),
            device_type=asset.device_type,
            site = Site.objects.first(),
            status = 'active',
        )

        form_data = {
            'name': 'test-device-assign',
            'device_type': asset.device_type.pk,
            'device': device.pk,
        }

        request = {
            'path': self._get_url('assign', asset),
            'data': post_data(form_data),
        }
        self.assertHttpStatus(self.client.post(**request), 302)

        devices = Device.objects.filter(name=device.name)
        self.assertEqual(len(devices), 1)
        self.assertEqual(devices.first().assigned_asset, asset)

    @override_settings(PLUGINS_CONFIG=CONFIG_ALLOW_CREATE_DEVICE_TYPE)
    def test_bulk_import_objects_with_permission(self):
        return super().test_bulk_import_objects_with_permission()

    @override_settings(PLUGINS_CONFIG=CONFIG_ALLOW_CREATE_DEVICE_TYPE)
    def test_bulk_import_objects_with_constrained_permission(self):
        return super().test_bulk_import_objects_with_constrained_permission()


class AssetBulkAddTestCase(
    ModelViewTestCase,
    ViewTestCases.CreateMultipleObjectsViewTestCase,
):
    """
    test for /plugins/inventory/assets/bulk-add/
    """
    model = Asset

    @classmethod
    def setUpTestData(cls):
        manufacturer1 = Manufacturer.objects.create(
            name='manufacturer1',
            slug='manufacturer1',
        )
        device_type1 = DeviceType.objects.create(
            model='device_type1',
            slug='device_type1',
            manufacturer=manufacturer1,
            u_height=1,
        )

        cls.bulk_create_data = {
            'count': 3,
            'status': 'stored',
            'device_type': device_type1.pk,
        }

    def _get_url(self, action, instance=None):
        # fix - CreateMultipleObjectsViewTestCase assumes view names contains only 'add' but we need 'bulk_add'
        if action == 'add':
            action = 'bulk_add'
        return super()._get_url(action, instance)

class AssetAssignBase():
    """
    Base class for tests that assign Asset to specific hardware
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
        self.asset_device = Asset.objects.create(
            asset_tag='asset_device',
            serial='asset_device',
            status='stored',
            device_type=self.device_type1,
        )
        self.asset_module = Asset.objects.create(
            asset_tag='asset_module',
            serial='asset_module',
            status='stored',
            module_type=self.module_type1,
        )
        self.asset_inventoryitem = Asset.objects.create(
            asset_tag='asset_inventoryitem',
            serial='asset_inventoryitem',
            status='stored',
            inventoryitem_type=self.inventoryitem_type1,
        )

    def _get_url(self, _):
        hardware_kind = self.tested_asset.kind
        if hardware_kind == 'inventoryitem':
            hardware_kind = 'inventory-item'
        return f'/plugins/inventory/assets/{hardware_kind}/create/?asset_id={self.tested_asset.pk}'

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_create_object_with_permission(self):
        super().test_create_object_with_permission()
        # in addition to a new inventoryitem instance in db,
        # it must have matching serial and asset2 must have it assigned
        instance = self._get_queryset().order_by('pk').last()
        self.assertEqual(instance.serial, self.tested_asset.serial)
        self.tested_asset.refresh_from_db()
        self.assertEqual(instance, self.tested_asset.hardware)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_create_object_with_constrained_permission(self):
        super().test_create_object_with_constrained_permission()
        # in addition to a new inventoryitem instance in db,
        # it must have matching serial and asset2 must have it assigned
        instance = self._get_queryset().order_by('pk').last()
        self.assertEqual(instance.serial, self.tested_asset.serial)
        self.tested_asset.refresh_from_db()
        self.assertEqual(instance, self.tested_asset.hardware)


class DeviceAssetAssignTestCase(AssetAssignBase, ModelViewTestCase, ViewTestCases.CreateObjectViewTestCase):
    """
    Test creating new Device from Asset
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
        self.tested_asset = self.asset_device


class ModuleAssetAssignTestCase(AssetAssignBase, ModelViewTestCase, ViewTestCases.CreateObjectViewTestCase):
    """
    Test creating new Module from Asset
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
        self.tested_asset = self.asset_module


class InventoryItemAssetAssignTestCase(AssetAssignBase, ModelViewTestCase, ViewTestCases.CreateObjectViewTestCase):
    """
    Test creating new InventoryItem from Asset
    """
    model = InventoryItem

    def setUp(self):
        super().setUp()
        self.form_data = {
            'device': self.device1.pk,
            'name': 'inventoryitem1',
        }
        self.tested_asset = self.asset_inventoryitem
