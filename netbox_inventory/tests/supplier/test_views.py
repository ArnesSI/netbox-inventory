from utilities.testing import ViewTestCases

from netbox_inventory.tests.custom import ModelViewTestCase
from netbox_inventory.models import Supplier


class SupplierTestCase(
    ModelViewTestCase,
    ViewTestCases.PrimaryObjectViewTestCase,
):

    model = Supplier

    form_data = {
        'name': 'Supplier',
        'slug': 'supplier',
        'description': 'supplier description',
    }
    csv_data = (
        'name,slug',
        'Supplier 4,supplier4',
        'Supplier 5,supplier5',
        'Supplier 6,supplier6',
    )
    bulk_edit_data = {
        'description': 'bulk description',
    }

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
        supplier3 = Supplier.objects.create(
            name='Supplier 3',
            slug='supplier3',
        )
        cls.csv_update_data = (
            'id,description',
            f'{supplier1.pk},description 1',
            f'{supplier2.pk},description 2',
            f'{supplier3.pk},description 3',
        )
