from utilities.testing import ViewTestCases

from netbox_inventory.tests.custom import ModelViewTestCase
from netbox_inventory.models import InventoryItemGroup


class InventoryItemGroupTestCase(
    ModelViewTestCase,
    ViewTestCases.PrimaryObjectViewTestCase,
):

    model = InventoryItemGroup

    form_data = {
        'name': 'InventoryItemGroup',
    }
    csv_data = (
        'name,comments',
        'IIG4,a comment',
        'IIG5,a comment',
        'IIG6,a comment',
    )

    @classmethod
    def setUpTestData(cls):
        iig1 = InventoryItemGroup.objects.create(name='IIG1')
        iig2 = InventoryItemGroup.objects.create(name='IIG2')
        iig3 = InventoryItemGroup.objects.create(name='IIG3')

        cls.csv_update_data = (
            'id,name,parent',
            f'{iig1.pk},IIG1_update,InventoryItemGroup',
            f'{iig2.pk},IIG2_update,InventoryItemGroup',
            f'{iig3.pk},IIG3_update,InventoryItemGroup',
        )
        cls.bulk_edit_data = {
            'comments': 'updated',
        }