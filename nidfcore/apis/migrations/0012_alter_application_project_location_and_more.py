# Generated by Django 5.1.5 on 2025-03-16 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0011_progressreport_activity_completed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='project_location',
            field=models.CharField(default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='application',
            name='type_of_church_project',
            field=models.CharField(blank=True, choices=[('REGIONAL HEADQUARTERS CHURCH', 'REGIONAL HEADQUARTERS CHURCH'), ('DIVISIONAL HEADQUARTERS CHURCH', 'DIVISIONAL HEADQUARTERS CHURCH'), ('GROUP OF DISTRICTS HEADQUARTERS CHURCH', 'GROUP OF DISTRICTS HEADQUARTERS CHURCH'), ('DISTRICT CHURCH', 'DISTRICT CHURCH'), ('LOCATION CHURCH', 'LOCATION CHURCH')], max_length=50, null=True),
        ),
    ]
