# documents/tasks.py
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.utils import timezone
from departments.models import DepartmentsDocuments

@shared_task
def upload_document(document_id):
    try:
        document = DepartmentsDocuments.objects.get(id=document_id)
        if document.upload_time <= timezone.now():
            # Logic to handle the upload
            document.published = True
            document.is_active = True
            document.save()
    except DepartmentsDocuments.DoesNotExist:
        pass
