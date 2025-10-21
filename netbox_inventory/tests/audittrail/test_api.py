from dcim.models import DeviceType, Manufacturer
from utilities.testing import APIViewTestCases

from netbox_inventory.models import Asset, AuditTrail, AuditTrailSource
from netbox_inventory.tests.custom import APITestCase


class AuditTrailTest(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = AuditTrail

    brief_fields = [
        'display',
        'id',
        'object',
        'url',
    ]

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
            Asset(
                asset_tag='asset4',
                serial='asset4',
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

        cls.create_data = [
            {
                'object_type': 'netbox_inventory.asset',
                'object_id': assets[0].pk,
            },
            {
                'object_type': 'netbox_inventory.asset',
                'object_id': assets[1].pk,
            },
            {
                'object_type': 'netbox_inventory.asset',
                'object_id': assets[2].pk,
            },
            # With source
            {
                'object_type': 'netbox_inventory.asset',
                'object_id': assets[0].pk,
                'source': audit_trail_source.pk,
            },
        ]

        cls.bulk_update_data = {
            'object_id': assets[3].pk,
        }
