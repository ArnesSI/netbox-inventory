from django.db import migrations

ROLE_NAME = 'Asset contact (migrated)'
ROLE_SLUG = 'asset-contact-migrated'


def contact_to_assignments(apps, schema_editor):
    """
    Move each Asset.contact into a ContactAssignment on that asset.

    The role is created only when there is something to migrate, so that
    installations that never used the field do not end up with an unused role.
    """
    Asset = apps.get_model('netbox_inventory', 'Asset')
    ContactAssignment = apps.get_model('tenancy', 'ContactAssignment')
    ContactRole = apps.get_model('tenancy', 'ContactRole')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    assets = Asset.objects.filter(contact__isnull=False).values_list(
        'pk', 'contact_id'
    )
    if not assets.exists():
        return

    role, _ = ContactRole.objects.get_or_create(
        slug=ROLE_SLUG,
        defaults={
            'name': ROLE_NAME,
            'description': 'Created when the asset contact field was replaced '
            'by contact assignments. Rename it, or reassign its contacts to '
            'other roles and delete it.',
        },
    )
    object_type, _ = ContentType.objects.get_or_create(
        app_label='netbox_inventory', model='asset'
    )
    ContactAssignment.objects.bulk_create(
        [
            ContactAssignment(
                object_type=object_type,
                object_id=asset_id,
                contact_id=contact_id,
                role=role,
            )
            for asset_id, contact_id in assets.iterator()
        ],
        ignore_conflicts=True,
    )


def assignments_to_contact(apps, schema_editor):
    """
    Reverse: put the migrated assignments back into Asset.contact.

    Only assignments carrying the migration role are moved back. Those are then
    deleted, and the role with them if nothing else uses it.
    """
    Asset = apps.get_model('netbox_inventory', 'Asset')
    ContactAssignment = apps.get_model('tenancy', 'ContactAssignment')
    ContactRole = apps.get_model('tenancy', 'ContactRole')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    role = ContactRole.objects.filter(slug=ROLE_SLUG).first()
    object_type = ContentType.objects.filter(
        app_label='netbox_inventory', model='asset'
    ).first()
    if role is None or object_type is None:
        return

    assignments = ContactAssignment.objects.filter(
        object_type=object_type, role=role
    ).order_by('pk')
    for assignment in assignments:
        # an asset holds a single contact, the oldest assignment wins
        Asset.objects.filter(pk=assignment.object_id, contact__isnull=True).update(
            contact_id=assignment.contact_id
        )
    assignments.delete()
    if not ContactAssignment.objects.filter(role=role).exists():
        role.delete()


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('netbox_inventory', '0021_alter_asset_owner_alter_assetrole_owner_and_more'),
        ('tenancy', '0022_add_comments_to_organizationalmodel'),
    ]

    operations = [
        migrations.RunPython(contact_to_assignments, assignments_to_contact),
        migrations.RemoveField(
            model_name='asset',
            name='contact',
        ),
    ]
