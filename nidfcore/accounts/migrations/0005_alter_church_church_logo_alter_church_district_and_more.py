# Generated by Django 5.1.5 on 2025-01-28 20:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_church_church_logo_alter_church_district_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='church',
            name='church_logo',
            field=models.ImageField(blank=True, null=True, upload_to='churches/logos/'),
        ),
        migrations.AlterField(
            model_name='church',
            name='district',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.district'),
        ),
        migrations.AlterField(
            model_name='church',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.region'),
        ),
    ]
