# Generated by Django 4.2.7 on 2024-05-07 04:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0010_rename_admin_adminuser_email'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='company_logo',
            new_name='logo',
        ),
        migrations.RenameField(
            model_name='company',
            old_name='company_name',
            new_name='name',
        ),
    ]
