from django.urls import path, include
from api import views
from rest_framework.routers import DefaultRouter
from djoser.views import UserViewSet

router = DefaultRouter()

router.register('departments', views.DepartmentModelViewSet, basename="department_api")
router.register('myTeams', views.CompanyTeamModelViewSet, basename="company_team_api")

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('', include(router.urls)),
]