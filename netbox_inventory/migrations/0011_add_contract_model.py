# Generated manually for netbox_inventory

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('netbox_inventory', '0010_asset_description_inventoryitemtype_description'),
        ('tenancy', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=None)),
                ('name', models.CharField(help_text='Contract name or identifier', max_length=100)),
                ('contract_id', models.CharField(blank=True, help_text='External contract identifier or number', max_length=50, null=True, verbose_name='Contract ID')),
                ('contract_type', models.CharField(choices=[('warranty', 'Warranty'), ('support', 'Support'), ('maintenance', 'Maintenance'), ('service', 'Service'), ('lease', 'Lease'), ('other', 'Other')], help_text='Type of contract', max_length=30, verbose_name='Contract Type')),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('active', 'Active'), ('expired', 'Expired'), ('cancelled', 'Cancelled'), ('renewed', 'Renewed')], help_text='Current status of the contract', max_length=30)),
                ('start_date', models.DateField(help_text='Date when the contract becomes effective', verbose_name='Start Date')),
                ('end_date', models.DateField(help_text='Date when the contract expires', verbose_name='End Date')),
                ('renewal_date', models.DateField(blank=True, help_text='Date when the contract is up for renewal', null=True, verbose_name='Renewal Date')),
                ('cost', models.DecimalField(blank=True, decimal_places=2, help_text='Total cost of the contract', max_digits=10, null=True)),
                ('currency', models.CharField(blank=True, help_text='Currency code (e.g., USD, EUR, GBP)', max_length=3)),
                ('contact', models.ForeignKey(blank=True, help_text='Primary contact for this contract', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='contracts', to='tenancy.contact')),
                ('description', models.CharField(blank=True, help_text='Brief description of the contract', max_length=200)),
                ('comments', models.TextField(blank=True, help_text='Additional comments or notes')),
                ('supplier', models.ForeignKey(help_text='Supplier providing the contract', on_delete=django.db.models.deletion.PROTECT, related_name='contracts', to='netbox_inventory.supplier')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='asset',
            name='contract',
            field=models.ForeignKey(blank=True, help_text='Contract associated with this asset', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='assets', to='netbox_inventory.contract'),
        ),
        migrations.AlterUniqueTogether(
            name='contract',
            unique_together={('supplier', 'contract_id')},
        ),
    ]