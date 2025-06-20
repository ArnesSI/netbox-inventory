from django.test import TestCase

from tenancy.filtersets import *
from tenancy.models import *
from utilities.testing import ChangeLoggedFilterSetTests

from netbox_inventory.filtersets import AuditTrailSourceFilterSet
from netbox_inventory.models import (
    AuditTrailSource,
)


class AuditTrailSourceTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = AuditTrailSource.objects.all()
    filterset = AuditTrailSourceFilterSet

    @classmethod
    def setUpTestData(cls):
        audit_trail_sources = (
            AuditTrailSource(
                name='Source 1',
                slug='source-1',
                description='Description 1',
            ),
            AuditTrailSource(
                name='Source 2',
                slug='source-2',
                description='Description 2',
            ),
            AuditTrailSource(
                name='Source 3',
                slug='source-3',
                description='Description 3',
            ),
        )
        AuditTrailSource.objects.bulk_create(audit_trail_sources)

    def test_q(self):
        params = {'q': 'Source 1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Source 1', 'Source 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['Description 1', 'Description 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
