# Generated by Django 5.0.6 on 2024-06-06 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='company_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
