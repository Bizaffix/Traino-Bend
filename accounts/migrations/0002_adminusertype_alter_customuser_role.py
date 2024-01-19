# Generated by Django 4.2.7 on 2023-11-19 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminUserType',
            fields=[
            ],
            options={
                'verbose_name': 'Admin',
                'verbose_name_plural': 'Admins',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('accounts.customuser',),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('Super Admin', 'Super Admin'), ('Admin', 'Admin'), ('Employee', 'Employee')], default='Super Admin', max_length=20),
        ),
    ]
