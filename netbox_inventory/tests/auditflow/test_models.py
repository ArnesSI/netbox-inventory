from dcim.models import Site

from netbox_inventory.models import AuditFlow
from netbox_inventory.tests.auditflowpage.test_models import BaseFlowModelTestCases


class TestAuditFlowModel(BaseFlowModelTestCases.ObjectFilterTestCase):
    model = AuditFlow

    model_data = {
        'name': 'Flow',
        'description': 'Flow description',
        'comments': 'Flow comments',
    }
    object_type = Site

    @classmethod
    def setUpTestData(cls) -> None:
        sites = (
            Site(
                name='Site 1',
                slug='site-1',
            ),
            Site(
                name='Site 2',
                slug='site-2',
            ),
        )
        Site.objects.bulk_create(sites)

        cls.object_filter = {
            'name': sites[0].name,
        }
