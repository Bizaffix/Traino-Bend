# Generated by Django 4.2.3 on 2023-11-22 18:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userdocuments',
            options={'verbose_name': 'Document', 'verbose_name_plural': 'Documents'},
        ),
    ]
