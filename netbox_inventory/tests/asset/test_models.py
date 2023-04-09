from django.test import override_settings, TestCase

from dcim.models import Device, DeviceType, DeviceRole, Manufacturer, Site
from utilities.exceptions import AbortRequest
from netbox_inventory.models import Asset
from ..settings import CONFIG_SYNC_OFF, CONFIG_SYNC_ON


class TestAssetModel(TestCase):
    def setUp(self):
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
        self.device_role1 = DeviceRole.objects.create(
            name='device_role1',
            slug='device_role1'
        )
        self.asset1 = Asset.objects.create(
            asset_tag='asset1',
            serial='asset1',
            status='stored',
            device_type=self.device_type1,
        )
        self.device1 = Device.objects.create(
            site=self.site1,
            status='active',
            device_type=self.device_type1,
            device_role=self.device_role1,
            name='device1',
        )
        self.device2 = Device.objects.create(
            site=self.site1,
            status='active',
            device_type=self.device_type1,
            device_role=self.device_role1,
            name='device2',
        )

    @override_settings(PLUGINS_CONFIG=CONFIG_SYNC_ON)
    def test_update_hardware_used_on(self):
        # assign device to asset
        self.asset1.snapshot()
        self.asset1.device=self.device1
        self.asset1.full_clean()
        self.asset1.save()
        self.assertEqual(self.device1.serial, self.asset1.serial)
        self.assertEqual(self.device1.asset_tag, self.asset1.asset_tag)
        
        # update asset serial updates device serial
        self.asset1.snapshot()
        self.asset1.serial = 'changed'
        self.asset1.full_clean()
        self.asset1.save()
        self.assertEqual(self.device1.serial, 'changed')
        
        # update device serial not allowed
        self.device1.snapshot()
        self.device1.serial = 'notallowed'
        self.device1.full_clean()
        with self.assertRaises(AbortRequest):
            self.device1.save()
        
        # assign defferent device
        self.assertEqual(self.asset1.device, self.device1)
        self.asset1.snapshot()
        self.asset1.device=self.device2
        self.asset1.full_clean()
        self.asset1.save()
        self.device1.refresh_from_db()
        self.device2.refresh_from_db()
        self.assertEqual(self.device1.serial, '')
        self.assertEqual(self.device1.asset_tag, None)
        self.assertEqual(self.device2.serial, self.asset1.serial)
        self.assertEqual(self.device2.asset_tag, self.asset1.asset_tag)

        # unassign device from asset
        self.asset1.snapshot()
        self.asset1.device = None
        self.asset1.full_clean()
        self.asset1.save()
        self.device1.refresh_from_db()
        self.device2.refresh_from_db()
        self.assertEqual(self.device1.serial, '')
        self.assertEqual(self.device1.asset_tag, None)
        self.assertEqual(self.device2.serial, '')
        self.assertEqual(self.device2.asset_tag, None)


    @override_settings(PLUGINS_CONFIG=CONFIG_SYNC_OFF)
    def test_update_hardware_used_off(self):
        # assign device to asset
        self.asset1.snapshot()
        self.asset1.device=self.device1
        self.asset1.full_clean()
        self.asset1.save()
        self.assertEqual(self.device1.serial, '')
        self.assertEqual(self.device1.asset_tag, None)
        
        # update asset serial updates device serial
        self.asset1.snapshot()
        self.asset1.serial = 'changed'
        self.asset1.full_clean()
        self.asset1.save()
        self.assertEqual(self.device1.serial, '')
        
        # update device serial is allowed
        self.device1.snapshot()
        self.device1.serial = 'allowed'
        self.device1.full_clean()
        self.device1.save()
        self.device1.refresh_from_db()
        self.assertEqual(self.device1.serial, 'allowed')

        # assign defferent device
        self.assertEqual(self.asset1.device, self.device1)
        self.asset1.snapshot()
        self.asset1.device=self.device2
        self.asset1.full_clean()
        self.asset1.save()
        self.device1.refresh_from_db()
        self.device2.refresh_from_db()
        self.assertEqual(self.device1.serial, 'allowed')
        self.assertEqual(self.device1.asset_tag, None)
        self.assertEqual(self.device2.serial, '')
        self.assertEqual(self.device2.asset_tag, None)

        # unassign device from asset
        self.asset1.snapshot()
        self.asset1.device = None
        self.asset1.full_clean()
        self.asset1.save()
        self.device1.refresh_from_db()
        self.device2.refresh_from_db()
        self.assertEqual(self.device1.serial, 'allowed')
        self.assertEqual(self.device1.asset_tag, None)
        self.assertEqual(self.device2.serial, '')
        self.assertEqual(self.device2.asset_tag, None)

    def test_update_status(self):
        self.asset1.snapshot()
        self.asset1.device = self.device1
        self.asset1.full_clean()
        self.asset1.save()
        self.asset1.refresh_from_db()
        self.assertEqual(self.asset1.status, 'used')
        self.asset1.snapshot()
        self.asset1.device = None
        self.asset1.full_clean()
        self.asset1.save()
        self.assertEqual(self.asset1.status, 'stored')

    def test_status_device_deleted(self):
        self.asset1.snapshot()
        self.asset1.device = self.device1
        self.asset1.full_clean()
        self.asset1.save()
        self.assertEqual(self.asset1.status, 'used')
        self.device1.delete()
        self.asset1.refresh_from_db()
        self.assertEqual(self.asset1.status, 'stored')
