from dcim.models import Manufacturer
from utilities.testing import APIViewTestCases

from ...models import InventoryItemType
from ..custom import APITestCase


class InventoryItemTypeTest(
    APITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = InventoryItemType
    brief_fields = [
        'description',
        'display',
        'id',
        'manufacturer',
        'model',
        'slug',
        'url',
    ]

    @classmethod
    def setUpTestData(cls) -> None:
        manufacturer1 = Manufacturer.objects.create(
            name='Manufacturer 1', slug='manufacturer1'
        )
        manufacturer2 = Manufacturer.objects.create(
            name='Manufacturer 2', slug='manufacturer2'
        )
        InventoryItemType.objects.create(
            model='InventoryItemType 1',
            slug='inventoryitemtype1',
            manufacturer=manufacturer1,
        )
        InventoryItemType.objects.create(
            model='InventoryItemType 2',
            slug='inventoryitemtype2',
            manufacturer=manufacturer1,
        )
        InventoryItemType.objects.create(
            model='InventoryItemType 3',
            slug='inventoryitemtype3',
            manufacturer=manufacturer1,
        )
        cls.create_data = [
            {
                'model': 'InventoryItemType 4',
                'slug': 'inventoryitemtype4',
                'manufacturer': manufacturer1.pk,
            },
            {
                'model': 'InventoryItemType 5',
                'slug': 'inventoryitemtype5',
                'manufacturer': manufacturer1.pk,
            },
            {
                'model': 'InventoryItemType 6',
                'slug': 'inventoryitemtype6',
                'manufacturer': manufacturer1.pk,
            },
        ]
        cls.bulk_update_data = {
            'manufacturer': manufacturer2.pk,
        }
