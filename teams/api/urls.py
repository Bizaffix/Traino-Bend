from django.urls import path
from .views import *

urlpatterns = [
    path('add-member/', AddMembersApiView.as_view(), name='Add-members'),
    path('member/<str:pk>/', MembersUpdateDestroyApiView.as_view(), name='Members-Update-Destroy'),
    path('member/', MembersListApiView.as_view(), name="members-list")
]
