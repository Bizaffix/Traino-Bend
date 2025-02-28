# Generated by Django 5.0.6 on 2024-08-08 16:41

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduleDetail',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('quiz_id', models.UUIDField()),
                ('question_id', models.UUIDField()),
                ('user_id', models.UUIDField()),
                ('department_id', models.UUIDField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
