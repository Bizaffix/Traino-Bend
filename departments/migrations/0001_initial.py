# Generated by Django 5.0.6 on 2024-07-25 20:44

import departments.models
import django.db.models.deletion
# import django_enum_choices.choice_builders
# import django_enum_choices.fields
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company', '0002_alter_company_company_id'),
        ('teams', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Departments',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('added_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='department_added_by_main', to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='department_company', to='company.company')),
                ('users', models.ManyToManyField(blank=True, to='teams.companiesteam')),
            ],
            options={
                'verbose_name': 'Company Department',
                'verbose_name_plural': 'Company Departments',
            },
        ),
        migrations.CreateModel(
            name='DepartmentsDocuments',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='media/documents/')),
                ('schedule_frequency', models.CharField(blank=True, max_length=50, null=True)),
                ('published', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('added_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='document_departments_added_by', to=settings.AUTH_USER_MODEL)),
                ('assigned_users', models.ManyToManyField(blank=True, related_name='assigned_documents', to='teams.companiesteam')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='document_departments', to='departments.departments')),
            ],
            options={
                'verbose_name': 'Company Document',
                'verbose_name_plural': 'Company Documents',
            },
        ),
    ]
