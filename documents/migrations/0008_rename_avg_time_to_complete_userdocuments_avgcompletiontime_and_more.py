# Generated by Django 5.0.6 on 2025-01-30 12:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0007_userdocuments_avg_time_to_complete_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userdocuments',
            old_name='avg_time_to_complete',
            new_name='avgCompletionTime',
        ),
        migrations.RenameField(
            model_name='userdocuments',
            old_name='duedate',
            new_name='dueDate',
        ),
    ]
