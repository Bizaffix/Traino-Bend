from django.urls import path
from .views import *

urlpatterns = [
    path('add-documents/', DepartmentsDocumentsCreateAPIView.as_view(), name='Add-documents'),
    path('documents/', DepartmentsDocumentsListAPIView.as_view(), name="documents-lists"),
    path('documents/<str:id>/', DepartmentsDocumentsUpdateDestroyRetrieveAPIView.as_view(), name="documents-RUD"),
    path('assign-document/<int:id>/', AssignDocumentsToUsersAPIView.as_view(), name='assign_document_to_users'),
]
