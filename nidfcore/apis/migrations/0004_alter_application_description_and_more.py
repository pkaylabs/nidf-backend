# Generated by Django 5.1.5 on 2025-01-28 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0003_application_updated_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='application',
            name='phase',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='application',
            name='purpose',
            field=models.TextField(blank=True, null=True),
        ),
    ]
