# Generated by Django 4.2.7 on 2024-05-05 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('departments', '0002_alter_departments_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='departments',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
