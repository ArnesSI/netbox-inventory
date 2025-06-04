# Generated manually for netbox_inventory

from django.db import migrations, models


def migrate_contract_data_forward(apps, schema_editor):
    """
    Migrate existing contract ForeignKey data to the new ManyToManyField.
    """
    Asset = apps.get_model('netbox_inventory', 'Asset')
    
    # Get all assets that have a contract assigned
    assets_with_contracts = Asset.objects.filter(contract_id__isnull=False)
    
    for asset in assets_with_contracts:
        # Add the existing contract to the new many-to-many relationship
        # Use contract_new since that's the temporary field name
        asset.contract_new.add(asset.contract_id)


def migrate_contract_data_reverse(apps, schema_editor):
    """
    Reverse migration: take the first contract from ManyToManyField and set it as ForeignKey.
    """
    Asset = apps.get_model('netbox_inventory', 'Asset')
    
    for asset in Asset.objects.all():
        contracts = asset.contract_new.all()
        if contracts.exists():
            # Set the first contract as the ForeignKey value
            asset.contract_id = contracts.first().id
            asset.save()


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_inventory', '0012_contract_add_contact_field'),
    ]

    operations = [
        # Step 1: Add the new ManyToManyField with a temporary name
        migrations.AddField(
            model_name='asset',
            name='contract_new',
            field=models.ManyToManyField(
                blank=True,
                help_text='Contracts associated with this asset',
                related_name='assets_new',
                to='netbox_inventory.contract',
                verbose_name='Contracts',
            ),
        ),
        
        # Step 2: Migrate data from old ForeignKey to new ManyToManyField
        migrations.RunPython(
            migrate_contract_data_forward,
            migrate_contract_data_reverse,
        ),
        
        # Step 3: Remove the old ForeignKey field
        migrations.RemoveField(
            model_name='asset',
            name='contract',
        ),
        
        # Step 4: Rename the new field to the original name
        migrations.RenameField(
            model_name='asset',
            old_name='contract_new',
            new_name='contract',
        ),
        
        # Step 5: Update the related_name to match the original
        migrations.AlterField(
            model_name='asset',
            name='contract',
            field=models.ManyToManyField(
                blank=True,
                help_text='Contracts associated with this asset',
                related_name='assets',
                to='netbox_inventory.contract',
                verbose_name='Contracts',
            ),
        ),
    ] 