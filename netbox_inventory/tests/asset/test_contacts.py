from core.models import ObjectType
from dcim.models import DeviceType, Manufacturer
from django.test import TestCase
from tenancy.choices import ContactPriorityChoices
from tenancy.models import Contact, ContactAssignment, ContactGroup, ContactRole

from netbox_inventory.filtersets import AssetFilterSet
from netbox_inventory.models import Asset
from netbox_inventory.tables import AssetTable


class AssetContactAssignmentTestCase(TestCase):
    """An asset can carry several contacts, each with its own role.

    Who uses an asset is one relationship. Others exist - who is accountable
    for it, which department it is charged to, the several people who share a
    meeting room machine - and ContactAssignment holds all of them.
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

    def test_contact_field_is_gone(self):
        """Contacts live in assignments only; there is no second place to look."""
        self.assertNotIn('contact', [f.name for f in Asset._meta.get_fields()])


class AssetContactFilterTestCase(TestCase):
    queryset = Asset.objects.all()
    filterset = AssetFilterSet

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )
        cls.assets = [
            Asset.objects.create(
                asset_tag=f'asset{i}', serial=f'serial{i}', status='stored', device_type=device_type
            )
            for i in range(1, 4)
        ]
        cls.groups = (
            ContactGroup.objects.create(name='Contact Group 1', slug='contact-group-1'),
            ContactGroup.objects.create(name='Contact Group 2', slug='contact-group-2'),
        )
        cls.contacts = (
            Contact.objects.create(name='Contact 1'),
            Contact.objects.create(name='Contact 2'),
        )
        cls.contacts[0].groups.add(cls.groups[0])
        cls.contacts[1].groups.add(cls.groups[1])
        cls.roles = (
            ContactRole.objects.create(name='Contact Role 1', slug='contact-role-1'),
            ContactRole.objects.create(name='Contact Role 2', slug='contact-role-2'),
        )
        object_type = ObjectType.objects.get_for_model(Asset)
        # asset1: contact 1 in two roles, asset2: contact 2, asset3: nobody
        for asset, contact, role in (
            (cls.assets[0], cls.contacts[0], cls.roles[0]),
            (cls.assets[0], cls.contacts[0], cls.roles[1]),
            (cls.assets[1], cls.contacts[1], cls.roles[1]),
        ):
            ContactAssignment.objects.create(
                object_type=object_type, object_id=asset.pk, contact=contact, role=role
            )

    def filter(self, **params):
        return self.filterset(params, self.queryset).qs

    def test_contact(self):
        self.assertQuerySetEqual(
            self.filter(contact=[self.contacts[0].pk]), [self.assets[0]]
        )
        self.assertEqual(
            self.filter(contact=[c.pk for c in self.contacts]).count(), 2
        )

    def test_contact_role(self):
        self.assertQuerySetEqual(
            self.filter(contact_role=[self.roles[0].pk]), [self.assets[0]]
        )
        self.assertEqual(self.filter(contact_role=[self.roles[1].pk]).count(), 2)

    def test_contact_group(self):
        self.assertQuerySetEqual(
            self.filter(contact_group=[self.groups[1].pk]), [self.assets[1]]
        )

    def test_contacts_column(self):
        table = AssetTable(Asset.objects.filter(pk=self.assets[0].pk))
        self.assertIn('contacts', table.columns.names())
        self.assertIn('Contact 1', str(table.rows[0].get_cell('contacts')))
