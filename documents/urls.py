from django.urls import path
from .views import *

urlpatterns = [
    path('add-document/', DepartmentsDocumentsCreateAPIView.as_view(), name='Add-documents'),
    path('documents/', DepartmentsDocumentsListAPIView.as_view(), name="documents-lists"),
    path('document/<str:id>/', DepartmentsDocumentsUpdateDestroyRetrieveAPIView.as_view(), name="documents-RUD"),
    path('assign-document/<int:id>/', AssignDocumentsToUsersAPIView.as_view(), name='assign_document_to_users'),
    path('update-schedule-details/', UpdateScheduleDetailsAPIView.as_view(), name='update_schedule_details')
    ]
