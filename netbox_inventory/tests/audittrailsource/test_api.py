from utilities.testing import APIViewTestCases

from netbox_inventory.models import AuditTrailSource
from netbox_inventory.tests.custom import APITestCase


class AuditTrailSourceTest(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = AuditTrailSource

    brief_fields = [
        'display',
        'id',
        'name',
        'slug',
        'url',
    ]

    create_data = [
        {'name': 'Source 4', 'slug': 'source-4'},
        {'name': 'Source 5', 'slug': 'source-5'},
        {'name': 'Source 6', 'slug': 'source-6'},
    ]

    bulk_update_data = {
        'description': 'new description',
    }

    @classmethod
    def setUpTestData(cls) -> None:
        audit_trail_sources = (
            AuditTrailSource(name='Source 1', slug='source-1'),
            AuditTrailSource(name='Source 2', slug='source-2'),
            AuditTrailSource(name='Source 3', slug='source-3'),
        )
        AuditTrailSource.objects.bulk_create(audit_trail_sources)
