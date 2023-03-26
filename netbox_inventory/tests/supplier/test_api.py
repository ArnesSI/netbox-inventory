from utilities.testing import APIViewTestCases
from ..custom import APITestCase
from ...models import Supplier


class SupplierTest(
        APITestCase, 
        APIViewTestCases.GetObjectViewTestCase,
        APIViewTestCases.ListObjectsViewTestCase,
        APIViewTestCases.CreateObjectViewTestCase,
        APIViewTestCases.UpdateObjectViewTestCase,
        APIViewTestCases.DeleteObjectViewTestCase):
    model = Supplier
    brief_fields = ['display', 'id', 'name', 'slug', 'url']
    create_data = [
        {
            'name': 'Supplier 4',
            'slug': 'supplier4',
        },
        {
            'name': 'Supplier 5',
            'slug': 'supplier5',
        },
        {
            'name': 'Supplier 6',
            'slug': 'supplier6',
        },
    ]
    bulk_update_data = {
        'description': 'new description',
    }

    @classmethod
    def setUpTestData(cls) -> None:
        Supplier.objects.create(name='Supplier 1', slug='supplier1')
        Supplier.objects.create(name='Supplier 2', slug='supplier2')
        Supplier.objects.create(name='Supplier 3', slug='supplier3')
