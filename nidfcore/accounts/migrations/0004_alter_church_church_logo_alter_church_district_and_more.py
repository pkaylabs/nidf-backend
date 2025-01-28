# Generated by Django 5.1.5 on 2025-01-28 20:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_rename_location_church_address_church_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='church',
            name='church_logo',
            field=models.ImageField(null=True, upload_to='churches/logos/'),
        ),
        migrations.AlterField(
            model_name='church',
            name='district',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.district'),
        ),
        migrations.AlterField(
            model_name='church',
            name='region',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.region'),
        ),
    ]
