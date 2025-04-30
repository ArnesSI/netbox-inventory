from django.test import override_settings
from django.urls import reverse

from utilities.testing import ViewTestCases

from netbox_inventory.models import AuditTrailSource
from netbox_inventory.tests.custom import ModelViewTestCase


class AuditTrailSourceViewTestCase(
    ModelViewTestCase,
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    model = AuditTrailSource

    form_data = {
        'name': 'Source',
        'slug': 'source',
        'description': 'Source description',
        'comments': 'Source comments',
    }

    csv_data = (
        'name,slug',
        'Source 4,source-4',
        'Source 5,source-5',
        'Source 6,source-6',
    )

    bulk_edit_data = {
        'description': 'Bulk description',
    }

    @classmethod
    def setUpTestData(cls) -> None:
        audit_trail_sources = (
            AuditTrailSource(name='Source 1', slug='source-1'),
            AuditTrailSource(name='Source 2', slug='source-2'),
            AuditTrailSource(name='Source 3', slug='source-3'),
        )
        AuditTrailSource.objects.bulk_create(audit_trail_sources)

        cls.csv_update_data = (
            'id,description',
            f'{audit_trail_sources[0].pk},description 1',
            f'{audit_trail_sources[1].pk},description 2',
            f'{audit_trail_sources[2].pk},description 3',
        )

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_view_audittrailsource_trails(self):
        audit_trail_source = AuditTrailSource.objects.first()

        url = reverse(
            'plugins:netbox_inventory:audittrailsource_trails',
            kwargs={'pk': audit_trail_source.pk},
        )
        self.assertHttpStatus(self.client.get(url), 200)
