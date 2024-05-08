from django.urls import path
from .views import LoginAPIView , CustomUserCreateAPIView , CustomUserUpdateAPIView


urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="user-details"),
    path('create-account/', CustomUserCreateAPIView.as_view(), name='signup'),
    path('update-account/<int:pk>/', CustomUserUpdateAPIView.as_view(), name="update"),
]
