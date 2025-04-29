from django.test import TestCase

from core.models import ObjectType
from dcim.models import DeviceType, Manufacturer
from tenancy.filtersets import *
from tenancy.models import *
from utilities.testing import ChangeLoggedFilterSetTests

from netbox_inventory.filtersets import AuditTrailFilterSet
from netbox_inventory.models import Asset, AuditTrail, AuditTrailSource


class AuditFlowTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = AuditTrail.objects.all()
    filterset = AuditTrailFilterSet

    @classmethod
    def setUpTestData(cls) -> None:
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
            ),
            Asset(
                asset_tag='asset2',
                serial='asset2',
                status='stored',
                device_type=device_type,
            ),
            Asset(
                asset_tag='asset3',
                serial='asset3',
                status='stored',
                device_type=device_type,
            ),
        )
        Asset.objects.bulk_create(assets)

        audit_trail_sources = (
            AuditTrailSource(
                name='Source 1',
                slug='source-1',
            ),
        )
        AuditTrailSource.objects.bulk_create(audit_trail_sources)

        audit_trails = (
            AuditTrail(object=assets[0], source=audit_trail_sources[0]),
            AuditTrail(object=assets[1]),
            AuditTrail(object=assets[2]),
            AuditTrail(object=device_type),
        )
        AuditTrail.objects.bulk_create(audit_trails)

    def test_object_type(self):
        params = {'object_type': 'netbox_inventory.asset'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

        object_type = ObjectType.objects.get_for_model(Asset)
        params = {'object_type_id': object_type.pk}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_source(self):
        audit_trail_source = AuditTrailSource.objects.first()

        params = {'source': [audit_trail_source.slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

        params = {'source_id': [audit_trail_source.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
