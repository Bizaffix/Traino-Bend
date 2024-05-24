# myapp/management/commands/activate_documents.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from departments.models import DepartmentsDocuments

class Command(BaseCommand):
    help = 'Activate scheduled documents'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        documents = DepartmentsDocuments.objects.filter(is_active=True, published=False, scheduled_time__lte=now)
        for document in documents:
            document.publish()
            self.stdout.write(self.style.SUCCESS(f'Document "{document.name}" activated.'))
