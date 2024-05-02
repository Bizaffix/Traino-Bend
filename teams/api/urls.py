from django.urls import path
from .views import *

urlpatterns = [
    path('add-members/', AddMembersApiView.as_view(), name='Add-members'),
    path('members/<str:pk>/', MembersUpdateDestroyApiView.as_view(), name='Members-Update-Destroy'),
    path('members/', MembersListApiView.as_view(), name="members-list")
]
