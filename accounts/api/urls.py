from django.urls import path
from .views import CustomUserDetailApiView


urlpatterns = [
    path("login/", CustomUserDetailApiView.as_view(), name="user-details")
]
