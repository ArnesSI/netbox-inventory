# Generated migration for NetBox 4.2.9 compatibility

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0013_contact_link'),
        ('netbox_inventory', '0011_add_contract_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='contact',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='contracts',
                to='tenancy.contact',
                verbose_name='Contact'
            ),
        ),
    ] 