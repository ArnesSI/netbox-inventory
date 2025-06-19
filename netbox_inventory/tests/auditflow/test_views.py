from django.contrib import messages
from django.contrib.messages.test import MessagesTestMixin
from django.db.models import Model
from django.http import HttpResponse
from django.test import override_settings
from django.urls import reverse

from core.models import ObjectType
from dcim.models import DeviceType, Location, Manufacturer, Site
from utilities.object_types import object_type_identifier
from utilities.testing import TestCase, ViewTestCases, post_data

from netbox_inventory.models import (
    Asset,
    AuditFlow,
    AuditFlowPage,
    AuditFlowPageAssignment,
    AuditTrail,
)
from netbox_inventory.tests.custom import ModelViewTestCase


class AuditFlowTestDataMixin(TestCase):
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

    def _run_audit_flow(
        self,
        audit_flow: AuditFlow,
        start_object: Model,
        method: str = 'get',
        expected_status: int = 200,
        **kwargs,
    ) -> HttpResponse:
        client = getattr(self.client, method)
        response = client(
            reverse(
                'plugins:netbox_inventory:auditflow_run',
                kwargs={'pk': audit_flow.pk},
            )
            + f'?object_id={start_object.pk}',
            **kwargs,
        )

        self.assertHttpStatus(response, expected_status)
        return response


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

        self._run_audit_flow(AuditFlow.objects.first(), Site.objects.first())


class AuditFlowRunTest(AuditFlowTestDataMixin, MessagesTestMixin, TestCase):
    user_permissions = [
        'dcim.view_site',
        'netbox_inventory.run_auditflow',
    ]

    def test_view_object_with_run_button(self) -> None:
        sites = Site.objects.order_by('name')
        audit_flow = AuditFlow.objects.first()

        # Limit flow to first site
        audit_flow.object_filter = {'name': sites[0].name}
        audit_flow.save()

        # Site 1: with button
        response = self.client.get(sites[0].get_absolute_url(), follow=True)
        self.assertHttpStatus(response, 200)
        self.assertIn(
            f'/audit-flows/{audit_flow.pk}/run/?object_id={sites[0].pk}',
            str(response.content),
        )

        # Site 2: No button displayed
        response = self.client.get(sites[1].get_absolute_url(), follow=True)
        self.assertHttpStatus(response, 200)
        self.assertNotIn(
            f'/audit-flows/{audit_flow.pk}/run/',
            str(response.content),
        )

    def test_add_object_button_hidden_if_no_permission(self) -> None:
        response = self._run_audit_flow(AuditFlow.objects.first(), Site.objects.first())

        # User has no permissions to add Asset.
        self.assertNotIn(
            reverse('plugins:netbox_inventory:asset_add'),
            str(response.content),
        )

    def test_add_object_button_params_location(self) -> None:
        self.add_permissions('netbox_inventory.add_asset')

        audit_flow = AuditFlow.objects.first()
        for site in Site.objects.all():
            with self.subTest(site=site.name):
                response = self._run_audit_flow(audit_flow, site)

                # Generic add button for Asset has site field pre-populated.
                self.assertIn(
                    f'storage_site={site.pk}',
                    str(response.content),
                )

    def test_add_object_button_params_variants(self, num_links: int = 4) -> None:
        self.add_permissions('netbox_inventory.add_asset')

        audit_flow = AuditFlow.objects.first()

        audit_flow_page: AuditFlowPage = audit_flow.pages.first()
        audit_flow_page.object_filter = {
            'status__in': ['stored', 'used', 'retired'],
            'device_type__manufacturer__name': 'Manufacturer 1',  # 1 option
            'device_type__model__startswith': 'DeviceType',  # 2 options
        }
        audit_flow_page.full_clean()
        audit_flow_page.save()

        # 4 options: 3 (status) + 1 (generic), no choices for device_type available
        response = self._run_audit_flow(audit_flow, Site.objects.first())
        self.assertEqual(
            str(response.content).count(reverse('plugins:netbox_inventory:asset_add')),
            num_links,
        )

    def test_add_object_button_params_variants_related_objects(self) -> None:
        manufacturer = Manufacturer.objects.create(
            name='Manufacturer 1',
            slug='manufacturer-1',
        )

        # 4 options: No increase as just one choice of Manufacturer
        self.test_add_object_button_params_variants()

        device_types = (
            DeviceType(
                manufacturer=manufacturer,
                model='DeviceType 1',
                slug='devicetype-1',
            ),
            DeviceType(
                manufacturer=manufacturer,
                model='DeviceType 2',
                slug='devicetype-2',
            ),
            DeviceType(
                manufacturer=manufacturer,
                model='Foo',  # Ignored by object_filter
                slug='foo',
            ),
        )
        DeviceType.objects.bulk_create(device_types)

        # 7 options: 3 (status) * 1 (manufacturer) * 2 (device type) + 1 generic
        self.test_add_object_button_params_variants(num_links=7)

    def test_audit_trail_button_hidden_if_no_permission(self) -> None:
        response = self._run_audit_flow(AuditFlow.objects.first(), Site.objects.first())

        # User has no permissions to mark objects as seen.
        self.assertNotIn(
            reverse('plugins:netbox_inventory:audittrail_bulk_add'),
            str(response.content),
        )

    def test_audit_trail_button(self) -> None:
        self.add_permissions('netbox_inventory.add_audittrail')
        self.add_permissions('netbox_inventory.delete_audittrail')

        site = Site.objects.first()
        location = Location(
            site=site,
            name='Location 1',
            slug='location-1',
            status='active',
        )
        location.full_clean()
        location.save()

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
                storage_location=location,
            ),
            Asset(
                asset_tag='asset2',
                serial='asset2',
                status='stored',
                device_type=device_type,
                storage_location=location,
            ),
            Asset(
                asset_tag='asset3',
                serial='asset3',
                status='stored',
                device_type=device_type,
                storage_location=location,
            ),
        )
        Asset.objects.bulk_create(assets)

        audit_trails = (
            AuditTrail(object=assets[0]),
            AuditTrail(object=assets[1]),
        )
        AuditTrail.objects.bulk_create(audit_trails)

        audit_flow = AuditFlow.objects.first()

        response = self._run_audit_flow(audit_flow, site)
        self.assertEqual(
            str(response.content).count(
                reverse('plugins:netbox_inventory:audittrail_bulk_add'),
            ),
            (
                (len(assets) - len(audit_trails))  # unseen
                + 1  # bulk mark seen button
            ),
        )

        for audit_trail in AuditTrail.objects.all():
            with self.subTest(audit_trail_for=audit_trail.pk):
                self.assertIn(
                    reverse(
                        'plugins:netbox_inventory:audittrail_delete',
                        kwargs={
                            'pk': audit_trail.pk,
                        },
                    ),
                    str(response.content),
                )

    def test_quick_search_mark_seen(self) -> None:
        self.add_permissions('netbox_inventory.add_audittrail')
        self.add_permissions('netbox_inventory.change_asset')

        sites = Site.objects.all()
        locations = (
            Location(
                site=sites[0],
                name='Location 1',
                slug='location-1',
                status='active',
            ),
            Location(
                site=sites[1],
                name='Location 2',
                slug='location-2',
                status='active',
            ),
        )
        for location in locations:
            location.full_clean()
            location.save()

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
                storage_location=locations[0],
            ),
            Asset(
                asset_tag='asset2',
                serial='asset2',
                status='stored',
                device_type=device_type,
                storage_location=locations[1],
            ),
        )
        Asset.objects.bulk_create(assets)

        audit_flow = AuditFlow.objects.first()

        # Single object found: mark as seen
        response = self._run_audit_flow(
            audit_flow,
            sites[0],
            method='post',
            data=post_data({'q': assets[0].serial}),
        )
        self.assertEqual(AuditTrail.objects.count(), 1)
        self.assertEqual(AuditTrail.objects.first().object, assets[0])

        # Object is at other site: Redirect to edit form
        response = self._run_audit_flow(
            audit_flow,
            sites[0],
            method='post',
            data=post_data({'q': 'asset2'}),
            expected_status=302,
        )
        redirect_url = (
            reverse(
                'plugins:netbox_inventory:auditflow_run',
                kwargs={'pk': audit_flow.pk},
            )
            + f'?object_id={sites[0].pk}'
        )
        self.assertRedirects(
            response,
            expected_url=reverse(
                'plugins:netbox_inventory:asset_edit',
                kwargs={'pk': assets[1].pk},
            )
            + f'?storage_site={sites[0].pk}&return_url={redirect_url}',
        )

        # No matching object found
        response = self._run_audit_flow(
            audit_flow,
            sites[0],
            method='post',
            data=post_data({'q': 'does-not-exist'}),
        )
        self.assertMessages(
            response,
            [
                messages.Message(messages.ERROR, 'No matching object found'),
            ],
        )
