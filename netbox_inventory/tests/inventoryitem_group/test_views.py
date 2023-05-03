from utilities.testing import ViewTestCases

from netbox_inventory.tests.custom import ModelViewTestCase
from netbox_inventory.models import InventoryItemGroup


class InventoryItemGroupTestCase(
    ModelViewTestCase,
    ViewTestCases.PrimaryObjectViewTestCase,
):

    model = InventoryItemGroup

    @classmethod
    def setUpTestData(cls):
        iig_parent = InventoryItemGroup.objects.create(name='parent group')
        iig1 = InventoryItemGroup.objects.create(name='IIG1')
        iig2 = InventoryItemGroup.objects.create(name='IIG2')
        iig3 = InventoryItemGroup.objects.create(name='IIG3')


        cls.form_data = {
            'name': 'InventoryItemGroup',
        }
        cls.csv_data = (
            'name,comments',
            'IIG4,a comment',
            'IIG5,a comment',
            'IIG6,a comment',
        )
        cls.csv_update_data = (
            'id,name,parent',
            f'{iig1.pk},IIG1_update,{iig_parent.name}',
            f'{iig2.pk},IIG2_update,{iig_parent.name}',
            f'{iig3.pk},IIG3_update,{iig_parent.name}',
        )
        cls.bulk_edit_data = {
            'comments': 'updated',
        }
