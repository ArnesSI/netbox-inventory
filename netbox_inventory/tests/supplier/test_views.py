from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from utilities.testing import ViewTestCases, create_tags
from tenancy.choices import ContactPriorityChoices
from tenancy.models import Contact, ContactRole, ContactAssignment

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


class ContactAssignmentTestCase(
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase
):
    model = ContactAssignment

    @classmethod
    def setUpTestData(cls):

        suppliers = (
            Supplier(name='Supplier 1', slug='supplier-1'),
            Supplier(name='Supplier 2', slug='supplier-2'),
            Supplier(name='Supplier 3', slug='supplier-3'),
            Supplier(name='Supplier 4', slug='supplier-4'),
        )
        Supplier.objects.bulk_create(suppliers)

        contacts = (
            Contact(name='Contact 1'),
            Contact(name='Contact 2'),
            Contact(name='Contact 3'),
            Contact(name='Contact 4'),
        )
        Contact.objects.bulk_create(contacts)

        contact_roles = (
            ContactRole(name='Contact Role 1', slug='contact-role-1'),
            ContactRole(name='Contact Role 2', slug='contact-role-2'),
            ContactRole(name='Contact Role 3', slug='contact-role-3'),
            ContactRole(name='Contact Role 4', slug='contact-role-4'),
        )
        ContactRole.objects.bulk_create(contact_roles)

        assignments = (
            ContactAssignment(
                object=suppliers[0],
                contact=contacts[0],
                role=contact_roles[0],
                priority=ContactPriorityChoices.PRIORITY_PRIMARY
            ),
            ContactAssignment(
                object=suppliers[1],
                contact=contacts[1],
                role=contact_roles[1],
                priority=ContactPriorityChoices.PRIORITY_SECONDARY
            ),
            ContactAssignment(
                object=suppliers[2],
                contact=contacts[2],
                role=contact_roles[2],
                priority=ContactPriorityChoices.PRIORITY_TERTIARY
            ),
        )
        ContactAssignment.objects.bulk_create(assignments)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'object_type': ContentType.objects.get_for_model(Supplier).pk,
            'object_id': suppliers[3].pk,
            'contact': contacts[3].pk,
            'role': contact_roles[3].pk,
            'priority': ContactPriorityChoices.PRIORITY_INACTIVE,
            'tags': [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            'role': contact_roles[3].pk,
            'priority': ContactPriorityChoices.PRIORITY_INACTIVE,
        }

    def _get_url(self, action, instance=None):
        # Override creation URL to append content_type & object_id parameters
        if action == 'add':
            url = reverse('tenancy:contactassignment_add')
            content_type = ContentType.objects.get_for_model(Supplier).pk
            object_id = Supplier.objects.first().pk
            return f"{url}?object_type={content_type}&object_id={object_id}"

        return super()._get_url(action, instance=instance)
