# Generated by Django 4.2.7 on 2024-05-08 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0016_alter_company_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='media/company_logos/'),
        ),
    ]
