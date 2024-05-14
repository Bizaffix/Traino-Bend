from django.urls import path
from .views import *

urlpatterns = [
    path('add-user/', AddMembersApiView.as_view(), name='Add-members'),
    path('user/<str:id>/', MembersUpdateDestroyApiView.as_view(), name='Members-Update-Destroy'),
    path('users/', MembersListApiView.as_view(), name="members-list"),
    path("bulk-users-delete/", BulkUserDeleteAPIView.as_view(), name="Bulk-Users-Delete")
]
