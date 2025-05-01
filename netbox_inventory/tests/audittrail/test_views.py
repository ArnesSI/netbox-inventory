from django.test import override_settings
from django.urls import reverse

from core.models import ObjectType
from dcim.models import DeviceType, Manufacturer
from users.models import ObjectPermission
from utilities.testing import ViewTestCases, post_data

from netbox_inventory.models import Asset, AuditTrail, AuditTrailSource
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

        audit_trail_source = AuditTrailSource.objects.create(
            name='Source 1',
            slug='source-1',
        )

        cls.csv_data = (
            'object_type,object_id',
            f'netbox_inventory.asset,{assets[0].pk}',
            f'netbox_inventory.asset,{assets[1].pk}',
            f'netbox_inventory.asset,{assets[2].pk}',
        )
        cls.csv_update_data = (
            'id,object_id,source',
            f'{audit_trails[0].pk},{assets[2].pk},{audit_trail_source.slug}',
            f'{audit_trails[1].pk},{assets[2].pk},{audit_trail_source.slug}',
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

    def test_bulk_add(self) -> None:
        """
        Check that objects can be marked seen in bulk (e.g. when running an audit flow).
        """
        self.add_permissions('netbox_inventory.add_audittrail')

        data = {
            'object_type_id': ObjectType.objects.get_for_model(Asset).pk,
            'pk': list(Asset.objects.values_list('pk', flat=True)),
        }

        request = {
            'path': reverse('plugins:netbox_inventory:audittrail_bulk_add'),
            'data': post_data(data),
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 302)
        self.assertEqual(
            AuditTrail.objects.count(),
            (
                len(data['pk'])  # new objects
                + 3  # from setUpTestData
            ),
        )

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_view_object_with_audit_trails(self) -> None:
        asset = Asset.objects.first()
        audit_trail_url = reverse(
            'plugins:netbox_inventory:asset_audit-trails',
            kwargs={'pk': asset.pk},
        )

        # Tab is visible
        response = self.client.get(asset.get_absolute_url(), follow=True)
        self.assertHttpStatus(response, 200)
        self.assertIn(audit_trail_url, str(response.content))

        # Tab is accessible
        response = self.client.get(audit_trail_url, follow=True)
        self.assertHttpStatus(response, 200)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_view_object_without_audit_trails(self) -> None:
        asset = Asset.objects.create(
            status='stored',
            device_type=DeviceType.objects.first(),
        )

        audit_trail_url = reverse(
            'plugins:netbox_inventory:asset_audit-trails',
            kwargs={'pk': asset.pk},
        )

        # Tab is not visible
        response = self.client.get(asset.get_absolute_url(), follow=True)
        self.assertHttpStatus(response, 200)
        self.assertNotIn(audit_trail_url, str(response.content))
