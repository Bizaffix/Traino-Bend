# Generated by Django 5.0.6 on 2024-07-25 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('departments', '0002_alter_departmentsdocuments_schedule_frequency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='departmentsdocuments',
            name='schedule_frequency',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]
