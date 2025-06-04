# Generated manually for netbox_inventory - Migration 0013

from django.db import migrations, models
import django.db.models.deletion


def migrate_contract_data_forward(apps, schema_editor):
    """
    Migrate existing contract ForeignKey data to the new ManyToManyField.
    Since the contract field might not have any data, this is a no-op.
    """
    Asset = apps.get_model('netbox_inventory', 'Asset')
    
    # Get all assets that have a contract assigned (if any)
    try:
        assets_with_contracts = Asset.objects.filter(contract_temp__isnull=False)
        
        for asset in assets_with_contracts:
            # Add the existing contract to the new many-to-many relationship
            asset.contract_new.add(asset.contract_temp_id)
    except:
        # If there's no data or field doesn't exist, just continue
        pass


def migrate_contract_data_reverse(apps, schema_editor):
    """
    Reverse migration: take the first contract from ManyToManyField and set it as ForeignKey.
    """
    Asset = apps.get_model('netbox_inventory', 'Asset')
    
    for asset in Asset.objects.all():
        contracts = asset.contract_new.all()
        if contracts.exists():
            # Set the first contract as the ForeignKey value
            asset.contract_temp_id = contracts.first().id
            asset.save()


class Migration(migrations.Migration):

    dependencies = [
        ('netbox_inventory', '0012_contract_add_contact_field'),
    ]

    operations = [
        # Step 1: Add a temporary ForeignKey field for contracts (in case it never existed)
        migrations.AddField(
            model_name='asset',
            name='contract_temp',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='assets_temp',
                to='netbox_inventory.contract',
                verbose_name='Contract',
            ),
        ),
        
        # Step 2: Add the new ManyToManyField with a temporary name
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
        
        # Step 3: Migrate data from old ForeignKey to new ManyToManyField (if any)
        migrations.RunPython(
            migrate_contract_data_forward,
            migrate_contract_data_reverse,
        ),
        
        # Step 4: Remove the temporary ForeignKey field
        migrations.RemoveField(
            model_name='asset',
            name='contract_temp',
        ),
        
        # Step 5: Rename the new field to the final name
        migrations.RenameField(
            model_name='asset',
            old_name='contract_new',
            new_name='contract',
        ),
        
        # Step 6: Update the related_name to match the final specification
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