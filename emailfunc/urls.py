from django.urls import path
from .views import SendEmailAPI

urlpatterns = [
    path('send-emails/', SendEmailAPI.as_view(), name='send_emails'),
]
