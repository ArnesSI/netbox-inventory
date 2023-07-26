from django.contrib.contenttypes.models import ContentType
from django.test import override_settings

from dcim.models import Manufacturer, DeviceType, DeviceRole, Device, Site
from users.models import ObjectPermission
from utilities.testing import post_data, ViewTestCases

from netbox_inventory.tests.custom import ModelViewTestCase
from netbox_inventory.models import Asset, Delivery, Purchase, Supplier
from ..settings import CONFIG_ALLOW_CREATE_DEVICE_TYPE


class AssetTestCase(
    ModelViewTestCase,
    ViewTestCases.PrimaryObjectViewTestCase,
):

    model = Asset

    @classmethod
    def setUpTestData(cls):
        supplier1 = Supplier.objects.create(
            name='Supplier1',
            slug='supplier1',
        )
        purchase1 = Purchase.objects.create(
            name='Purchase1',
            supplier=supplier1,
        )
        purchase2 = Purchase.objects.create(
            name='Purchase2',
            supplier=supplier1,
        )
        delivery1 = Delivery.objects.create(
            name='the_delivery',
            purchase=purchase1,
        )
        delivery2 = Delivery.objects.create(
            name='the_delivery',
            purchase=purchase2,
        )
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
            'serial,status,hardware_kind,manufacturer,model_name,supplier,purchase,delivery',
            'csv1,stored,device,manufacturer1,device_type1,Supplier1,Purchase1,the_delivery',
            'csv2,stored,device,manufacturer1,device_type1,Supplier1,Purchase1,the_delivery',
            'csv3,stored,device,manufacturer_csv,device_type_csv,,,',
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
    def test_assign_device_from_asset(self):

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

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_purchase_delivery_autoset(self):
        """
        check that assigning delivery without purchase auto-sets purchase
        """
        # Assign unconstrained permission
        obj_perm = ObjectPermission(
            name='test-asset permission',
            actions=['add', 'change']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        supplier1 = Supplier.objects.create(
            name='Supplier1-autoset',
            slug='supplier1-autoset',
        )
        purchase1 = Purchase.objects.create(
            name='Purchase1-autoset',
            supplier=supplier1,
        )
        delivery1 = Delivery.objects.create(
            name='Delivery1-autoset',
            purchase=purchase1,
        )

        form_data = {
            'status': 'stored',
            'serial': '123delivery',
            'device_type': DeviceType.objects.first(),
            'delivery': delivery1.pk,
        }

        request = {
            'path': self._get_url('add'),
            'data': post_data(form_data),
        }
        self.assertHttpStatus(self.client.post(**request), 302)

        assets = Asset.objects.filter(serial='123delivery')
        self.assertEqual(len(assets), 1)
        self.assertEqual(assets.first().purchase, purchase1)


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
