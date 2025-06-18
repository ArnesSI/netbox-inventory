from django.core.exceptions import ValidationError
from django.test import TestCase

from core.models import ObjectType
from dcim.models import DeviceType, InterfaceTemplate, Manufacturer

from netbox_inventory.models import Asset, AuditFlowPage
from netbox_inventory.models.audit import BaseFlow


class BaseFlowModelTestCases:
    class ObjectFilterTestCase(TestCase):
        def _get_flow_object(self) -> BaseFlow:
            return self.model(
                object_type=ObjectType.objects.get_for_model(self.object_type),
                **self.model_data,
            )

        def test_clean_object_filter(self) -> None:
            # No error
            obj = self._get_flow_object()
            obj.object_filter = self.object_filter
            obj.full_clean()

            # Filter is not a dictionary
            obj.object_filter = 'foo'
            self.assertRaises(ValidationError, obj.full_clean)

            # Filter is invalid
            obj.object_filter = {'field-does-not-exist': 'foo'}
            self.assertRaises(ValidationError, obj.full_clean)

        def test_get_objects_type(self) -> None:
            obj = self._get_flow_object()
            self.assertEqual(obj.get_objects().model, self.object_type)

        def test_get_objects_filter(self) -> None:
            # No filter
            obj = self._get_flow_object()
            self.assertEqual(
                obj.get_objects().count(),
                self.object_type.objects.count(),
            )

            # Filter objects
            obj.object_filter = self.object_filter
            self.assertEqual(
                obj.get_objects().count(),
                self.object_type.objects.filter(**self.object_filter).count(),
            )


class TestAuditFlowPageModel(BaseFlowModelTestCases.ObjectFilterTestCase):
    model = AuditFlowPage

    model_data = {
        'name': 'Page',
        'description': 'Page description',
        'comments': 'Page comments',
    }
    object_type = Asset

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
        )
        Asset.objects.bulk_create(assets)

        cls.object_filter = {
            'asset_tag': assets[0].asset_tag,
        }

    def test_clean_object_type(self) -> None:
        # No error
        page1 = AuditFlowPage(
            name='Page 1',
            object_type=ObjectType.objects.get_for_model(Asset),
        )
        page1.full_clean()

        # No list view
        page2 = AuditFlowPage(
            name='Page 1',
            object_type=ObjectType.objects.get_for_model(InterfaceTemplate),
        )
        self.assertRaises(ValidationError, page2.full_clean)
