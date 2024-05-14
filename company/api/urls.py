from django.urls import path
from .views import *

urlpatterns = [
    path('create-admin/', CreateAdminApiView.as_view(), name="create-admin"),
    path('create-company/', CompanyCreateApiView.as_view(), name='Create_Company'),
    path('company/<str:id>/', CompanyUpdateAndDeleteApiView.as_view(), name='Update_Delete_Company'),
    path('companies/', CompanyListApiView.as_view(), name='Detailed_Company'),
    path('admin/<str:id>/', AdminUserUpdateAndDeleteApiView.as_view(), name='admin-details'),
    path('admins/', AdminListApiView.as_view(), name='admins-list'),
    path('bulk-admins-delete/', BulkAdminDeleteAPIView.as_view(), name="Bulk_Admins_delete")
]
