# Generated by Django 4.0.8 on 2022-10-27 16:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('netbox_inventory', '0001_initial_prod'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='serial',
            field=models.CharField(blank=True, default=None, max_length=60, null=True),
        ),
    ]
