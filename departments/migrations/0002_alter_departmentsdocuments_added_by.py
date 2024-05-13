# Generated by Django 4.2.7 on 2024-05-13 06:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('departments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='departmentsdocuments',
            name='added_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='document_departments_added_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
