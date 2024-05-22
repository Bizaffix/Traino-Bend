# Generated by Django 2.1.7 on 2024-05-22 07:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('departments', '0001_initial'),
        ('accounts', '0001_initial'),
        ('company', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentKeyPoints',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('content', models.TextField(blank=True, null=True)),
                ('prompt_text', models.CharField(blank=True, max_length=255, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('added_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='keypoint_added_by', to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='keypoint_company', to='company.company')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='departments.DepartmentsDocuments')),
            ],
            options={
                'verbose_name': 'Keypoints',
                'verbose_name_plural': 'Keypoints',
            },
        ),
        migrations.CreateModel(
            name='DocumentQuiz',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('content', models.TextField(blank=True, null=True)),
                ('prompt_text', models.CharField(blank=True, max_length=255, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('added_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='quiz_added_by', to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quiz_company', to='company.company')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='departments.DepartmentsDocuments')),
            ],
            options={
                'verbose_name': 'Quiz',
                'verbose_name_plural': 'Quizes',
            },
        ),
        migrations.CreateModel(
            name='DocumentSummary',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('content', models.TextField(blank=True, null=True)),
                ('prompt_text', models.CharField(blank=True, max_length=255, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('added_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='summary_added_by', to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='summary_company', to='company.company')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='summary_document', to='departments.DepartmentsDocuments')),
            ],
            options={
                'verbose_name': 'Summary',
                'verbose_name_plural': 'Summary',
            },
        ),
        migrations.CreateModel(
            name='DocumentTeam',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('is_assigned', models.BooleanField(default=False)),
                ('notify_frequency', models.CharField(default='0', max_length=2)),
                ('department', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='assignee_department', to='accounts.Departments')),
            ],
        ),
        migrations.CreateModel(
            name='QuizQuestions',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('question', models.CharField(blank=True, max_length=255, null=True)),
                ('option_1', models.CharField(blank=True, max_length=255, null=True)),
                ('option_2', models.CharField(blank=True, max_length=255, null=True)),
                ('option_3', models.CharField(blank=True, max_length=255, null=True)),
                ('option_4', models.CharField(blank=True, max_length=255, null=True)),
                ('answer', models.CharField(blank=True, max_length=2, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('added_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='quiz_question_added_by', to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quiz_question_company', to=settings.AUTH_USER_MODEL)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='departments.DepartmentsDocuments')),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='documents.DocumentQuiz')),
            ],
            options={
                'verbose_name': 'Question',
                'verbose_name_plural': 'Questions',
            },
        ),
        migrations.CreateModel(
            name='UserDocuments',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, null=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='documents/')),
                ('published', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('added_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='document_added_by', to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='document_company', to=settings.AUTH_USER_MODEL)),
                ('department', models.ManyToManyField(related_name='document_departments', to='accounts.Departments')),
            ],
            options={
                'verbose_name': 'Company Document',
                'verbose_name_plural': 'Company Documents',
            },
        ),
        migrations.AddField(
            model_name='documentteam',
            name='document',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='assignee_document', to='documents.UserDocuments'),
        ),
        migrations.AddField(
            model_name='documentteam',
            name='user',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='assignee_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
