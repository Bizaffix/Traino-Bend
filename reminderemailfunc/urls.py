from django.urls import path
from .views import SendEmailAPI

urlpatterns = [
    path('reminder-send-emails/', SendEmailAPI.as_view(), name='send_emails'),
]
