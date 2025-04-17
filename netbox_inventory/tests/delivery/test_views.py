import datetime

from utilities.testing import ViewTestCases

from netbox_inventory.models import Delivery, Purchase, Supplier
from netbox_inventory.tests.custom import ModelViewTestCase


class DeliveryTestCase(
    ModelViewTestCase,
    ViewTestCases.PrimaryObjectViewTestCase,
):
    model = Delivery

    @classmethod
    def setUpTestData(cls):
        supplier1 = Supplier.objects.create(
            name='Supplier 1',
            slug='supplier1',
        )
        supplier2 = Supplier.objects.create(
            name='Supplier 2',
            slug='supplier2',
        )
        purchase1 = Purchase.objects.create(
            name='Purchase 1',
            supplier=supplier1,
            status='closed',
        )
        purchase2 = Purchase.objects.create(
            name='Purchase 1',
            supplier=supplier2,
            status='closed',
        )
        delivery1 = Delivery.objects.create(name='Delivery 1')
        delivery1.purchases.set([purchase1])
        delivery2 = Delivery.objects.create(name='Delivery 2')
        delivery2.purchases.set([purchase1])
        delivery3 = Delivery.objects.create(name='Delivery 3')
        delivery3.purchases.set([purchase2])
        cls.form_data = {
            'name': 'Delivery',
            'purchases': [purchase1.pk],
            'description': 'Delivery description',
            'date': datetime.date(day=1, month=1, year=2023),
        }
        cls.csv_data = (
            'name,purchases,date',
            f'Delivery 4,{purchase1.pk},2023-03-26',
            f'Delivery 5,{purchase1.pk},2023-03-26',
            f'Delivery 6,{purchase1.pk},2023-03-26',
        )
        cls.csv_update_data = (
            'id,description,purchases',
            f'{delivery1.pk},description 1,{delivery1.purchases.first().pk}',
            f'{delivery2.pk},description 2,{delivery2.purchases.first().pk}',
            f'{delivery3.pk},description 3,{delivery3.purchases.first().pk}',
        )
        cls.bulk_edit_data = {
            'description': 'bulk description',
            'date': datetime.date(day=1, month=1, year=2022),
        }
