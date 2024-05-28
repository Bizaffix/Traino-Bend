from django.urls import path
from .views import LoginAPIView , CustomUserCreateAPIView , CustomUserUpdateAPIView , UserDetailAPIView


urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path('auths/users/me/', UserDetailAPIView.as_view(), name='user-detail'),
    path('create-account/', CustomUserCreateAPIView.as_view(), name='signup'),
    path('update-account/<str:id>/', CustomUserUpdateAPIView.as_view(), name="update"),
]
