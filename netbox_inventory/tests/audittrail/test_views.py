from django.urls import reverse

from core.models import ObjectType
from dcim.models import DeviceType, Manufacturer
from users.models import ObjectPermission
from utilities.testing import ViewTestCases

from netbox_inventory.models import Asset, AuditTrail
from netbox_inventory.tests.custom import ModelViewTestCase


class AuditTrailViewTestCase(
    ModelViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    model = AuditTrail

    @classmethod
    def setUpTestData(cls) -> None:
        manufacturer = Manufacturer.objects.create(
            name='manufacturer 1',
            slug='manufacturer-1',
        )
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='DeviceType 1',
            slug='devicetype-1',
        )

        assets = (
            Asset(
                asset_tag='asset1',
                serial='asset1',
                status='stored',
                device_type=device_type,
            ),
            Asset(
                asset_tag='asset2',
                serial='asset2',
                status='stored',
                device_type=device_type,
            ),
            Asset(
                asset_tag='asset3',
                serial='asset3',
                status='stored',
                device_type=device_type,
            ),
        )
        Asset.objects.bulk_create(assets)

        audit_trails = (
            AuditTrail(object=assets[0]),
            AuditTrail(object=assets[1]),
            AuditTrail(object=assets[2]),
        )
        AuditTrail.objects.bulk_create(audit_trails)

        cls.csv_data = (
            'object_type,object_id',
            f'netbox_inventory.asset,{assets[0].pk}',
            f'netbox_inventory.asset,{assets[1].pk}',
            f'netbox_inventory.asset,{assets[2].pk}',
        )
        cls.csv_update_data = (
            'id,object_id',
            f'{audit_trails[0].pk},{assets[2].pk}',
            f'{audit_trails[1].pk},{assets[2].pk}',
        )

    def test_list_objects_with_constrained_permission(self) -> None:
        """
        Test object-level permissions for the `AuditTrail` model. A custom test is used
        because the default test case checks for the model's URL. However, `AuditTrail`
        objects don't have a detail view. The delete object URL is used instead.
        """
        self.add_permissions('netbox_inventory.delete_audittrail')

        instance1, instance2 = self._get_queryset().all()[:2]

        # Add object-level permission
        obj_perm = ObjectPermission(
            name='Test permission', constraints={'pk': instance1.pk}, actions=['view']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

        # Try GET with object-level permission
        response = self.client.get(self._get_url('list'))
        self.assertHttpStatus(response, 200)
        content = str(response.content)
        self.assertIn(
            reverse('plugins:netbox_inventory:audittrail_delete', args=[instance1.pk]),
            content,
        )
        self.assertNotIn(
            reverse('plugins:netbox_inventory:audittrail_delete', args=[instance2.pk]),
            content,
        )
