from core.models import ObjectType
from utilities.object_types import object_type_identifier
from utilities.testing import ViewTestCases

from netbox_inventory.models import Asset, AuditFlowPage
from netbox_inventory.tests.custom import ModelViewTestCase


class AuditFlowPageViewTestCase(
    ModelViewTestCase,
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    model = AuditFlowPage

    @classmethod
    def setUpTestData(cls) -> None:
        object_type = ObjectType.objects.get_for_model(Asset)

        page1 = AuditFlowPage.objects.create(
            name='Page 1',
            object_type=object_type,
        )
        page2 = AuditFlowPage.objects.create(
            name='Page 2',
            object_type=object_type,
        )
        page3 = AuditFlowPage.objects.create(
            name='Page 3',
            object_type=object_type,
        )

        cls.form_data = {
            'name': 'Page',
            'description': 'Page description',
            'object_type': object_type.pk,
            'object_filter': '{"status": "stored"}',
            'comments': 'Page comments',
        }
        cls.csv_data = (
            'name,object_type',
            f'Page 4,{object_type_identifier(object_type)}',
            f'Page 5,{object_type_identifier(object_type)}',
            f'Page 6,{object_type_identifier(object_type)}',
        )
        cls.csv_update_data = (
            'id,description',
            f'{page1.pk},description 1',
            f'{page2.pk},description 2',
            f'{page3.pk},description 3',
        )
