# Generated by Django 5.1.5 on 2025-03-17 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0013_application_is_emergency'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='expected_completion_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
