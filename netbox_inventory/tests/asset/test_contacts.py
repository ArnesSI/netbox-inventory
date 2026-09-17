from core.models import ObjectType
from dcim.models import DeviceType, Manufacturer
from django.test import TestCase
from tenancy.choices import ContactPriorityChoices
from tenancy.models import Contact, ContactAssignment, ContactRole

from netbox_inventory.models import Asset


class AssetContactAssignmentTestCase(TestCase):
    """An asset can carry several contacts, each with its own role.

    The `contact` field says who uses an asset. Other relationships exist -
    who is accountable for it, which department it is charged to, the several
    people who share a meeting room machine - and they are what
    ContactAssignment is for.
    """

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )
        cls.asset = Asset.objects.create(
            asset_tag='asset1', serial='serial1', status='stored', device_type=device_type
        )
        cls.contacts = (
            Contact.objects.create(name='Contact 1'),
            Contact.objects.create(name='Contact 2'),
        )
        cls.role = ContactRole.objects.create(name='Contact Role 1', slug='contact-role-1')

    def test_asset_object_type_supports_contacts(self):
        self.assertIn('contacts', ObjectType.objects.get_for_model(Asset).features)

    def test_assignment_validates_and_is_readable_from_the_asset(self):
        assignment = ContactAssignment(
            object_type=ObjectType.objects.get_for_model(Asset),
            object_id=self.asset.pk,
            contact=self.contacts[0],
            role=self.role,
            priority=ContactPriorityChoices.PRIORITY_PRIMARY,
        )
        assignment.full_clean()
        assignment.save()

        self.assertEqual(self.asset.contacts.count(), 1)
        self.assertEqual(self.asset.get_contacts().first().contact, self.contacts[0])

    def test_several_contacts_on_one_asset(self):
        object_type = ObjectType.objects.get_for_model(Asset)
        for contact, priority in zip(
            self.contacts,
            (ContactPriorityChoices.PRIORITY_PRIMARY, ContactPriorityChoices.PRIORITY_SECONDARY),
        ):
            ContactAssignment(
                object_type=object_type,
                object_id=self.asset.pk,
                contact=contact,
                role=self.role,
                priority=priority,
            ).save()

        self.assertEqual(self.asset.contacts.count(), 2)

    def test_contact_field_is_unaffected(self):
        """The existing single field keeps working; nothing migrates itself."""
        self.asset.contact = self.contacts[0]
        self.asset.save()
        self.asset.refresh_from_db()
        self.assertEqual(self.asset.contact, self.contacts[0])
        self.assertEqual(self.asset.contacts.count(), 0)
