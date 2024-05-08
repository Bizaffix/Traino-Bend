from django.urls import path
from .views import *

urlpatterns = [
    path('add-user/', AddMembersApiView.as_view(), name='Add-members'),
    path('user/<str:pk>/', MembersUpdateDestroyApiView.as_view(), name='Members-Update-Destroy'),
    path('users/', MembersListApiView.as_view(), name="members-list")
]
