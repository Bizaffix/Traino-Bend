# Generated by Django 4.2.7 on 2024-05-07 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0012_alter_company_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='logo',
            field=models.ImageField(blank=True, default='OneColumbia.jpeg', null=True, upload_to='company_logos/'),
        ),
    ]
