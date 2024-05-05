from django.urls import path
from .views import *

urlpatterns = [
    path('add-documents/', DepartmentsDocumentsCreateAPIView.as_view(), name='Add-documents'),
    path('documents/', DepartmentsDocumentsListAPIView.as_view(), name="documents-lists"),
    path('documents/<str:id>/', DepartmentsDocumentsUpdateDestroyRetrieveAPIView.as_view(), name="documents-RUD")
]
