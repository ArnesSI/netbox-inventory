from utilities.testing import APIViewTestCases
from ..custom import APITestCase
from ...models import Delivery, Purchase, Supplier


class DeliveryTest(
        APITestCase, 
        APIViewTestCases.GetObjectViewTestCase,
        APIViewTestCases.ListObjectsViewTestCase,
        APIViewTestCases.CreateObjectViewTestCase,
        APIViewTestCases.UpdateObjectViewTestCase,
        APIViewTestCases.DeleteObjectViewTestCase):
    model = Delivery
    brief_fields = ['date', 'display', 'id', 'name', 'url']

    bulk_update_data = {
        'description': 'new description',
    }

    @classmethod
    def setUpTestData(cls) -> None:
        supplier1 = Supplier.objects.create(name='Supplier1', slug='supplier1')
        purchase1 = Purchase.objects.create(name='Purchase1', supplier=supplier1)
        Delivery.objects.create(name='Delivery 1', purchase=purchase1)
        Delivery.objects.create(name='Delivery 2', purchase=purchase1)
        Delivery.objects.create(name='Delivery 3', purchase=purchase1)
        cls.create_data = [
            {
                'name': 'Delivery 4',
                'purchase': purchase1.pk,
            },
            {
                'name': 'Delivery 5',
                'purchase': purchase1.pk,
            },
            {
                'name': 'Delivery 6',
                'purchase': purchase1.pk,
            },
        ]
