from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from departments.models import DepartmentsDocuments

def activate_scheduled_documents():
    now = timezone.now()
    documents = DepartmentsDocuments.objects.filter(is_active=True, published=False, scheduled_time__lte=now)
    for document in documents:
        document.published = True
        document.save()

def start():
    scheduler = BackgroundScheduler()
    # Run the job every minute
    scheduler.add_job(activate_scheduled_documents, 'interval', minutes=1)
    scheduler.start()
    # print("Scheduler started...")