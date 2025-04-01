from django.test import override_settings
from django.urls import reverse

from core.models import ObjectType
from dcim.models import Site
from utilities.object_types import object_type_identifier
from utilities.testing import ViewTestCases

from netbox_inventory.models import (
    Asset,
    AuditFlow,
    AuditFlowPage,
    AuditFlowPageAssignment,
)
from netbox_inventory.tests.custom import ModelViewTestCase


class AuditFlowViewTestCase(
    ModelViewTestCase,
    ViewTestCases.PrimaryObjectViewTestCase,
):
    model = AuditFlow

    @classmethod
    def setUpTestData(cls) -> None:
        object_type = ObjectType.objects.get_for_model(Site)

        flow1 = AuditFlow.objects.create(
            name='Flow 1',
            object_type=object_type,
        )
        flow2 = AuditFlow.objects.create(
            name='Flow 2',
            object_type=object_type,
        )
        flow3 = AuditFlow.objects.create(
            name='Flow 3',
            object_type=object_type,
        )

        cls.form_data = {
            'name': 'Flow',
            'description': 'Flow description',
            'enabled': False,
            'object_type': object_type.pk,
            'object_filter': '{"name": "Site 1"}',
            'comments': 'Flow comments',
        }
        cls.csv_data = (
            'name,object_type',
            f'Flow 4,{object_type_identifier(object_type)}',
            f'Flow 5,{object_type_identifier(object_type)}',
            f'Flow 6,{object_type_identifier(object_type)}',
        )
        cls.csv_update_data = (
            'id,description',
            f'{flow1.pk},description 1',
            f'{flow2.pk},description 2',
            f'{flow3.pk},description 3',
        )
        cls.bulk_edit_data = {
            'enabled': False,
        }

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_auditflow_pages(self):
        object_type = ObjectType.objects.get_for_model(Asset)
        audit_flow_pages = (
            AuditFlowPage(name='Page 1', object_type=object_type),
            AuditFlowPage(name='Page 2', object_type=object_type),
            AuditFlowPage(name='Page 3', object_type=object_type),
        )
        AuditFlowPage.objects.bulk_create(audit_flow_pages)

        audit_flow = AuditFlow.objects.first()
        audit_flow_page_assignments = (
            AuditFlowPageAssignment(flow=audit_flow, page=audit_flow_pages[0]),
            AuditFlowPageAssignment(flow=audit_flow, page=audit_flow_pages[1]),
            AuditFlowPageAssignment(flow=audit_flow, page=audit_flow_pages[2]),
        )
        AuditFlowPageAssignment.objects.bulk_create(audit_flow_page_assignments)

        url = reverse(
            'plugins:netbox_inventory:auditflow_pages',
            kwargs={'pk': audit_flow.pk},
        )
        self.assertHttpStatus(self.client.get(url), 200)
