from core.models import ObjectType
from dcim.models import Site
from utilities.object_types import object_type_identifier
from utilities.testing import APIViewTestCases

from netbox_inventory.models import AuditFlow
from netbox_inventory.tests.custom import APITestCase


class AuditFlowTest(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = AuditFlow

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
        object_type = ObjectType.objects.get_for_model(Site)

        AuditFlow.objects.create(
            name='Flow 1',
            object_type=object_type,
        )
        AuditFlow.objects.create(
            name='Flow 2',
            object_type=object_type,
        )
        AuditFlow.objects.create(
            name='Flow 3',
            object_type=object_type,
        )

        cls.create_data = [
            {
                'name': 'Flow 4',
                'object_type': object_type_identifier(object_type),
            },
            {
                'name': 'Flow 5',
                'object_type': object_type_identifier(object_type),
            },
            {
                'name': 'Flow 6',
                'object_type': object_type_identifier(object_type),
            },
        ]
