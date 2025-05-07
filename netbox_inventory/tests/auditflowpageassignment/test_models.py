from django.core.exceptions import ValidationError
from django.test import TestCase

from core.models import ObjectType
from dcim.models import DeviceType, Location, Manufacturer, Site

from netbox_inventory.models import (
    Asset,
    AuditFlow,
    AuditFlowPage,
    AuditFlowPageAssignment,
)


class TestAuditFlowPageAssignmentModel(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        site = Site.objects.create(
            name='Site 1',
            slug='site-1',
        )
        cls.locations = (
            Location(
                site=site,
                name='Location 1',
                slug='location-1',
                status='active',
            ),
            Location(
                site=site,
                name='Location 2',
                slug='location-2',
                status='active',
            ),
        )
        for location in cls.locations:
            location.full_clean()
            location.save()

        cls.audit_flows = (
            AuditFlow(
                name='Flow 1',
                object_type=ObjectType.objects.get_for_model(Location),
            ),
        )
        AuditFlow.objects.bulk_create(cls.audit_flows)

        cls.audit_flow_pages = (
            AuditFlowPage(
                name='Page 1',
                object_type=ObjectType.objects.get_for_model(Asset),
            ),
        )
        AuditFlowPage.objects.bulk_create(cls.audit_flow_pages)

    def test_clean_filter_lookup(self) -> None:
        # No Error
        obj = AuditFlowPageAssignment(
            flow=self.audit_flows[0],
            page=self.audit_flow_pages[0],
        )
        obj.full_clean()

        # No filter lookup path available
        page2 = AuditFlowPage.objects.create(
            name='Page 2',
            object_type=ObjectType.objects.get_for_model(DeviceType),
        )
        obj = AuditFlowPageAssignment(flow=self.audit_flows[0], page=page2)
        self.assertRaises(ValidationError, obj.full_clean)

    def test_get_objects_type(self) -> None:
        obj = AuditFlowPageAssignment(
            flow=self.audit_flows[0],
            page=self.audit_flow_pages[0],
        )
        self.assertEqual(obj.get_objects(self.locations[0]).model, Asset)

    def test_get_objects_location(self) -> None:
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
                storage_location=self.locations[0],
            ),
            Asset(
                asset_tag='asset2',
                serial='asset2',
                status='stored',
                device_type=device_type,
                storage_location=self.locations[1],
            ),
        )
        Asset.objects.bulk_create(assets)

        location = self.locations[0]
        objects = AuditFlowPageAssignment(
            flow=self.audit_flows[0],
            page=self.audit_flow_pages[0],
        ).get_objects(location)
        self.assertEqual(objects.count(), 1)
        self.assertEqual(objects.first().storage_location, location)

    def test_get_objects_nested(self) -> None:
        manufacturer = Manufacturer.objects.create(
            name='manufacturer 1',
            slug='manufacturer-1',
        )
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='DeviceType 1',
            slug='devicetype-1',
        )

        parent_location = self.locations[0]
        child_location = Location(
            site=parent_location.site,
            name='Child Location 1',
            slug='child-location-1',
            status='active',
            parent=parent_location,
        )
        child_location.full_clean()
        child_location.save()

        assets = (
            Asset(
                asset_tag='asset1',
                serial='asset1',
                status='stored',
                device_type=device_type,
                storage_location=parent_location,
            ),
            Asset(
                asset_tag='asset2',
                serial='asset2',
                status='stored',
                device_type=device_type,
                storage_location=child_location,
            ),
        )
        Asset.objects.bulk_create(assets)

        objects = (
            AuditFlowPageAssignment(
                flow=self.audit_flows[0],
                page=self.audit_flow_pages[0],
            )
            .get_objects(parent_location)
            .order_by('pk')
        )
        self.assertEqual(objects.count(), 2)
        self.assertEqual(objects[0].storage_location, parent_location)
        self.assertEqual(objects[1].storage_location, child_location)
