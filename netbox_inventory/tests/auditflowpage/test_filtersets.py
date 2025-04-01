from django.test import TestCase

from core.models import ObjectType
from dcim.models import Device
from tenancy.filtersets import *
from tenancy.models import *
from utilities.testing import ChangeLoggedFilterSetTests

from netbox_inventory.filtersets import AuditFlowPageFilterSet
from netbox_inventory.models import Asset, AuditFlowPage


class AuditFlowPageTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = AuditFlowPage.objects.all()
    filterset = AuditFlowPageFilterSet
    ignore_fields = ('object_filter',)

    @classmethod
    def setUpTestData(cls):
        cls.object_types = (
            ObjectType.objects.get_for_model(Asset),
            ObjectType.objects.get_for_model(Device),
        )

        AuditFlowPage.objects.create(
            name='Page 1',
            description='Description 1',
            object_type=cls.object_types[0],
        )
        AuditFlowPage.objects.create(
            name='Page 2',
            description='Description 2',
            object_type=cls.object_types[1],
        )
        AuditFlowPage.objects.create(
            name='Page 3',
            description='Description 3',
            object_type=cls.object_types[1],
        )

    def test_q(self):
        params = {'q': 'Page 1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Page 1', 'Page 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['Description 1', 'Description 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_object_type(self):
        params = {'object_type': 'netbox_inventory.asset'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

        params = {'object_type_id': [self.object_types[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
