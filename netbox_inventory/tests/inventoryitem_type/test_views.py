from dcim.models import Manufacturer
from utilities.testing import ViewTestCases

from netbox_inventory.tests.custom import ModelViewTestCase
from netbox_inventory.models import InventoryItemType, InventoryItemGroup


class InventoryItemTypeTestCase(
    ModelViewTestCase,
    ViewTestCases.PrimaryObjectViewTestCase,
):

    model = InventoryItemType

    @classmethod
    def setUpTestData(cls):
        manufacturer1 = Manufacturer.objects.create(
            name='Manufacturer 1',
            slug='manufacturer1',
        )
        manufacturer2 = Manufacturer.objects.create(
            name='Manufacturer 2',
            slug='manufacturer2',
        )
        inventoryitem_group1 = InventoryItemGroup.objects.create(name='IIG1')
        inventoryitemtype1 = InventoryItemType.objects.create(
            model='InventoryItemType 1',
            slug='inventoryitemtype1',
            manufacturer=manufacturer1,
        )
        inventoryitemtype2 = InventoryItemType.objects.create(
            model='InventoryItemType 2',
            slug='inventoryitemtype2',
            manufacturer=manufacturer1,
        )
        inventoryitemtype3 = InventoryItemType.objects.create(
            model='InventoryItemType 3',
            slug='inventoryitemtype3',
            manufacturer=manufacturer1,
        )
        cls.form_data = {
            'model': 'InventoryItemType',
            'slug': 'inventoryitemtype',
            'manufacturer': manufacturer1.pk,
            'part_number': 'InventoryItemType PN',
        }
        cls.csv_data = (
            'model,slug,manufacturer',
            f'InventoryItemType 4,inventoryitemtype4,{manufacturer1.name}',
            f'InventoryItemType 5,inventoryitemtype5,{manufacturer1.name}',
            f'InventoryItemType 6,inventoryitemtype6,{manufacturer1.name}',
        )
        cls.csv_update_data = (
            'id,manufacturer',
            f'{inventoryitemtype1.pk},{manufacturer2.name}',
            f'{inventoryitemtype2.pk},{manufacturer2.name}',
            f'{inventoryitemtype3.pk},{manufacturer2.name}',
        )
        cls.bulk_edit_data = {
            'inventoryitem_group': inventoryitem_group1.pk,
        }
