from django.contrib.contenttypes.models import ContentType
from dcim.models import Device, DeviceRole, DeviceType, InventoryItem, Manufacturer, ModuleType, Site
from users.models import ObjectPermission
from utilities.testing import APIViewTestCases, disable_warnings
from rest_framework import status

from ..custom import APITestCase
from ...models import Asset, InventoryItemType


class AssetTest(
        APITestCase, 
        APIViewTestCases.GetObjectViewTestCase,
        APIViewTestCases.ListObjectsViewTestCase,
        APIViewTestCases.CreateObjectViewTestCase,
        APIViewTestCases.UpdateObjectViewTestCase,
        APIViewTestCases.DeleteObjectViewTestCase):
    model = Asset
    brief_fields = ['display', 'id', 'serial', 'url']

    bulk_update_data = {
        'status': 'used',
    }

    def test_assign_device_matching_device_type(self):
        """
        check assigning device to asset when asset's & device's device_type matches
        """
        # Add object-level permission
        obj_perm = ObjectPermission(
            name='Test permission',
            actions=['add', 'change']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        update_data = {'device':self.device1.pk}

        response = self.client.post(self._get_list_url(), self.create_data[0], format='json', **self.header)
        instance = self._get_queryset().get(pk=response.data['id'])
        url = self._get_detail_url(instance)
        response = self.client.patch(url, update_data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        instance.refresh_from_db()
        self.assertInstanceEqual(
            instance,
            update_data,
            exclude=self.validation_excluded_fields,
            api=True
        )

    def test_assign_device_missmatch_device_type(self):
        """
        check assigning device to asset when asset's & device's device_type doesn't match
        """
        # Add object-level permission
        obj_perm = ObjectPermission(
            name='Test permission',
            actions=['add', 'change']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        update_data = {'device':self.device2.pk}

        response = self.client.post(self._get_list_url(), self.create_data[0], format='json', **self.header)
        instance = self._get_queryset().get(pk=response.data['id'])
        url = self._get_detail_url(instance)
        response = self.client.patch(url, update_data, format='json', **self.header)
        with disable_warnings('django.request'):
            self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

    def test_assign_inventoryitem_to_asset_device(self):
        """
        check assigning inventoryitem to asset when asset.kind is device
        """
        # Add object-level permission
        obj_perm = ObjectPermission(
            name='Test permission',
            actions=['add', 'change']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        update_data = {'inventoryitem':self.inventoryitem1.pk}

        response = self.client.post(self._get_list_url(), self.create_data[0], format='json', **self.header)
        instance = self._get_queryset().get(pk=response.data['id'])
        url = self._get_detail_url(instance)
        response = self.client.patch(url, update_data, format='json', **self.header)
        with disable_warnings('django.request'):
            self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer1')
        device_type1 = DeviceType.objects.create(model='Device Type 1', slug='devicetype1', manufacturer=manufacturer)
        device_type2 = DeviceType.objects.create(model='Device Type 2', slug='devicetype2', manufacturer=manufacturer)
        module_type1 = ModuleType.objects.create(model='Module Type 1', manufacturer=manufacturer)
        inventoryitem_type1 = InventoryItemType.objects.create(model='II Type 1', manufacturer=manufacturer)
        site1 = Site.objects.create(name='Site 1', slug='site1')
        device_role1 = DeviceRole.objects.create(name='Device Role 1', slug='devicerole1')
        cls.device1 = Device.objects.create(name='Device 1', device_role=device_role1, device_type=device_type1, site=site1, status='active')
        cls.device2 = Device.objects.create(name='Device 2', device_role=device_role1, device_type=device_type2, site=site1, status='active')
        cls.inventoryitem1 = InventoryItem.objects.create(device=cls.device1, name='II 1')

        Asset.objects.create(name='Asset 1', serial='asset1', device_type=device_type1)
        Asset.objects.create(name='Asset 2', serial='asset2', device_type=device_type1)
        Asset.objects.create(name='Asset 3', serial='asset3', device_type=device_type1)

        cls.create_data = [
            {
                'name': 'Asset 4',
                'serial': 'asset4',
                'status': 'stored',
                'device_type': device_type1.pk,
                'device': None,
            },
            {
                'name': 'Asset 5',
                'serial': 'asset5',
                'status': 'stored',
                'device_type': None,
                'device': None,
                'module_type': module_type1.pk,
                'module': None,
            },
            {
                'name': 'Asset 6',
                'serial': 'asset6',
                'status': 'stored',
                'inventoryitem_type': inventoryitem_type1.pk,
                'inventoryitem': cls.inventoryitem1.pk,
            },
        ]
