from django.test import override_settings
from django.urls import reverse

from core.models import ObjectType
from dcim.models import Site
from utilities.object_types import object_type_identifier
from utilities.testing import TestCase, ViewTestCases

from netbox_inventory.models import (
    Asset,
    AuditFlow,
    AuditFlowPage,
    AuditFlowPageAssignment,
)
from netbox_inventory.tests.custom import ModelViewTestCase


class AuditFlowTestDataMixin:
    @classmethod
    def setUpTestData(cls) -> None:
        cls.sites = (
            Site(
                name='Site 1',
                slug='site-1',
            ),
            Site(
                name='Site 2',
                slug='site-2',
            ),
        )
        Site.objects.bulk_create(cls.sites)

        object_type_site = ObjectType.objects.get_for_model(Site)
        audit_flows = (
            AuditFlow(
                name='Flow 1',
                object_type=object_type_site,
            ),
            AuditFlow(
                name='Flow 2',
                object_type=object_type_site,
            ),
            AuditFlow(
                name='Flow 3',
                object_type=object_type_site,
            ),
        )
        AuditFlow.objects.bulk_create(audit_flows)

        object_type_asset = ObjectType.objects.get_for_model(Asset)
        audit_flow_pages = (
            AuditFlowPage(name='Page 1', object_type=object_type_asset),
            AuditFlowPage(name='Page 2', object_type=object_type_asset),
            AuditFlowPage(name='Page 3', object_type=object_type_asset),
        )
        AuditFlowPage.objects.bulk_create(audit_flow_pages)

        audit_flow_page_assignments = (
            AuditFlowPageAssignment(flow=audit_flows[0], page=audit_flow_pages[0]),
            AuditFlowPageAssignment(flow=audit_flows[0], page=audit_flow_pages[1]),
            AuditFlowPageAssignment(flow=audit_flows[0], page=audit_flow_pages[2]),
        )
        AuditFlowPageAssignment.objects.bulk_create(audit_flow_page_assignments)


class AuditFlowViewTestCase(
    AuditFlowTestDataMixin,
    ModelViewTestCase,
    ViewTestCases.PrimaryObjectViewTestCase,
):
    model = AuditFlow

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        object_type = ObjectType.objects.get_for_model(Site)
        audit_flows = AuditFlow.objects.order_by('name')

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
            f'{audit_flows[0].pk},description 1',
            f'{audit_flows[1].pk},description 2',
            f'{audit_flows[2].pk},description 3',
        )
        cls.bulk_edit_data = {
            'enabled': False,
        }

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_auditflow_pages(self):
        audit_flow = AuditFlow.objects.first()

        url = reverse(
            'plugins:netbox_inventory:auditflow_pages',
            kwargs={'pk': audit_flow.pk},
        )
        self.assertHttpStatus(self.client.get(url), 200)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_auditflow_run(self):
        self.add_permissions('netbox_inventory.run_auditflow')

        audit_flow = AuditFlow.objects.first()
        site = Site.objects.first()

        url = (
            reverse(
                'plugins:netbox_inventory:auditflow_run',
                kwargs={'pk': audit_flow.pk},
            )
            + f'?object_id={site.pk}'
        )
        self.assertHttpStatus(self.client.get(url), 200)


class AuditFlowRunTest(AuditFlowTestDataMixin, TestCase):
    user_permissions = [
        'dcim.view_site',
        'netbox_inventory.run_auditflow',
    ]

    def test_view_object_with_run_button(self):
        sites = Site.objects.order_by('name')
        audit_flow = AuditFlow.objects.first()

        # Limit flow to first site
        audit_flow.object_filter = {'name': sites[0].name}
        audit_flow.save()

        # Site 1: with button
        response = self.client.get(sites[0].get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            f'/audit-flows/{audit_flow.pk}/run/?object_id={sites[0].pk}',
            str(response.content),
        )

        # Site 2: No button displayed
        response = self.client.get(sites[1].get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            f'/audit-flows/{audit_flow.pk}/run/',
            str(response.content),
        )
