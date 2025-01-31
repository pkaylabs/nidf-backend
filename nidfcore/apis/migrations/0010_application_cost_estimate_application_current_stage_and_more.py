# Generated by Django 5.1.5 on 2025-01-31 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0009_progressreport_updated_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='cost_estimate',
            field=models.FileField(blank=True, null=True, upload_to='applications/cost_estimate/'),
        ),
        migrations.AddField(
            model_name='application',
            name='current_stage',
            field=models.FileField(blank=True, null=True, upload_to='applications/current_stage/'),
        ),
        migrations.AddField(
            model_name='application',
            name='invoices',
            field=models.FileField(blank=True, null=True, upload_to='applications/invoices/'),
        ),
        migrations.AddField(
            model_name='application',
            name='land_ownership',
            field=models.FileField(blank=True, null=True, upload_to='applications/land_ownership/'),
        ),
    ]
