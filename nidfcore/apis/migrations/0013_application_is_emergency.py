# Generated by Django 5.1.5 on 2025-03-17 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0012_alter_application_project_location_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='is_emergency',
            field=models.BooleanField(default=False),
        ),
    ]
