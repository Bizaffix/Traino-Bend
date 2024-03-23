from django.urls import path, include
from api import views
from rest_framework.routers import DefaultRouter
from djoser.views import UserViewSet

router = DefaultRouter()

router.register('departments', views.DepartmentModelViewSet, basename="department_api")
router.register('myTeams', views.CompanyTeamModelViewSet, basename="company_team_api")
router.register('myLearnings', views.DocumentModelViewSet, basename="company_document_api")
router.register('summary', views.DocumentSummaryModelViewSet, basename="company_document_summary_api")
router.register('keypoints', views.DocumentKeypointsModelViewSet, basename="company_document_keypoints_api")

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('', include(router.urls)),
]