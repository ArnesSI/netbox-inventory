from core.models import ObjectType
from utilities.object_types import object_type_identifier
from utilities.testing import APIViewTestCases

from netbox_inventory.models import Asset, AuditFlowPage
from netbox_inventory.tests.custom import APITestCase


class AuditFlowPageTest(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = AuditFlowPage

    brief_fields = [
        'display',
        'id',
        'name',
        'url',
    ]

    bulk_update_data = {
        'description': 'new description',
    }

    @classmethod
    def setUpTestData(cls) -> None:
        object_type = ObjectType.objects.get_for_model(Asset)

        AuditFlowPage.objects.create(
            name='Page 1',
            object_type=object_type,
        )
        AuditFlowPage.objects.create(
            name='Page 2',
            object_type=object_type,
        )
        AuditFlowPage.objects.create(
            name='Page 3',
            object_type=object_type,
        )

        cls.create_data = [
            {
                'name': 'Page 4',
                'object_type': object_type_identifier(object_type),
            },
            {
                'name': 'Page 5',
                'object_type': object_type_identifier(object_type),
            },
            {
                'name': 'Page 6',
                'object_type': object_type_identifier(object_type),
            },
        ]
