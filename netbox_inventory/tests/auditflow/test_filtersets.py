from django.test import TestCase

from core.models import ObjectType
from dcim.models import Location, Site
from tenancy.filtersets import *
from tenancy.models import *
from utilities.testing import ChangeLoggedFilterSetTests

from netbox_inventory.filtersets import AuditFlowFilterSet
from netbox_inventory.models import (
    Asset,
    AuditFlow,
    AuditFlowPage,
    AuditFlowPageAssignment,
)


class AuditFlowTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = AuditFlow.objects.all()
    filterset = AuditFlowFilterSet
    ignore_fields = (
        'object_filter',
        'pages',
    )

    @classmethod
    def setUpTestData(cls):
        cls.object_types = (
            ObjectType.objects.get_for_model(Site),
            ObjectType.objects.get_for_model(Location),
        )

        cls.audit_flows = (
            AuditFlow(
                name='Flow 1',
                description='Description 1',
                object_type=cls.object_types[0],
            ),
            AuditFlow(
                name='Flow 2',
                description='Description 2',
                object_type=cls.object_types[1],
            ),
            AuditFlow(
                name='Flow 3',
                description='Description 3',
                object_type=cls.object_types[1],
            ),
        )
        AuditFlow.objects.bulk_create(cls.audit_flows)

    def test_q(self):
        params = {'q': 'Flow 1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Flow 1', 'Flow 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['Description 1', 'Description 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_object_type(self):
        params = {'object_type': 'dcim.site'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

        params = {'object_type_id': [self.object_types[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_page(self):
        audit_flow_pages = (
            AuditFlowPage.objects.create(
                name='Page 1',
                object_type=ObjectType.objects.get_for_model(Asset),
            ),
        )
        AuditFlowPageAssignment.objects.create(
            flow=self.audit_flows[0],
            page=audit_flow_pages[0],
        )

        params = {'page_id': [audit_flow_pages[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
