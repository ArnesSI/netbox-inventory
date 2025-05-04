from core.models import ObjectType
from dcim.models import Site
from utilities.testing import APIViewTestCases

from netbox_inventory.models import (
    Asset,
    AuditFlow,
    AuditFlowPage,
    AuditFlowPageAssignment,
)
from netbox_inventory.tests.custom import APITestCase


class AuditFlowPageAssignmentTest(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = AuditFlowPageAssignment

    brief_fields = [
        'display',
        'flow',
        'id',
        'page',
        'url',
    ]

    bulk_update_data = {
        'weight': 500,
    }

    @classmethod
    def setUpTestData(cls) -> None:
        audit_flows = (
            AuditFlow(
                name='Flow 1',
                object_type=ObjectType.objects.get_for_model(Site),
            ),
        )
        AuditFlow.objects.bulk_create(audit_flows)

        object_type = ObjectType.objects.get_for_model(Asset)
        audit_flow_pages = (
            AuditFlowPage(name='Page 1', object_type=object_type),
            AuditFlowPage(name='Page 2', object_type=object_type),
            AuditFlowPage(name='Page 3', object_type=object_type),
            AuditFlowPage(name='Page 4', object_type=object_type),
            AuditFlowPage(name='Page 5', object_type=object_type),
            AuditFlowPage(name='Page 6', object_type=object_type),
        )
        AuditFlowPage.objects.bulk_create(audit_flow_pages)

        audit_flow_page_assignments = (
            AuditFlowPageAssignment(flow=audit_flows[0], page=audit_flow_pages[0]),
            AuditFlowPageAssignment(flow=audit_flows[0], page=audit_flow_pages[1]),
            AuditFlowPageAssignment(flow=audit_flows[0], page=audit_flow_pages[2]),
        )
        AuditFlowPageAssignment.objects.bulk_create(audit_flow_page_assignments)

        cls.create_data = (
            {
                'flow': audit_flows[0].pk,
                'page': audit_flow_pages[3].pk,
            },
            {
                'flow': audit_flows[0].pk,
                'page': audit_flow_pages[4].pk,
            },
            {
                'flow': audit_flows[0].pk,
                'page': audit_flow_pages[5].pk,
            },
        )
