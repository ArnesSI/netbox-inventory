from copy import deepcopy
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings

from dcim.models import Manufacturer, DeviceType, DeviceRole, Device, Site
from users.models import ObjectPermission
from utilities.testing import post_data, ViewTestCases

from netbox_inventory.tests.custom import ModelViewTestCase
from netbox_inventory.models import Asset


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
            'serial,status,hardware_kind,manufacturer,hardware_type',
            'csv1,stored,device,manufacturer1,device_type1',
            'csv2,stored,device,manufacturer1,device_type1',
            'csv3,stored,device,manufacturer_csv,device_type_csv',
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
