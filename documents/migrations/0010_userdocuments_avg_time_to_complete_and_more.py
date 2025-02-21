# Generated by Django 5.0.6 on 2025-02-21 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0009_remove_userdocuments_avgcompletiontime_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdocuments',
            name='avg_time_to_complete',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userdocuments',
            name='duedate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userdocuments',
            name='overview',
            field=models.TextField(blank=True, null=True),
        ),
    ]
