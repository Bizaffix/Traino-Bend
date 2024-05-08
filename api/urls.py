from django.urls import path, include
from api import views
from rest_framework.routers import DefaultRouter
from djoser.views import UserViewSet
from .views import DepartmentCreateApiview, DepartmentListApiView , DepartmentRetrieveApiView, CompanyDepartmentsListAPIView


router = DefaultRouter()

router.register('myTeams', views.CompanyTeamModelViewSet, basename="company_team_api")
router.register('myLearnings', views.DocumentModelViewSet, basename="company_document_api")
router.register('summary', views.DocumentSummaryModelViewSet, basename="company_document_summary_api")
router.register('keypoints', views.DocumentKeypointsModelViewSet, basename="company_document_keypoints_api")

urlpatterns = [
    path('create-department/', DepartmentCreateApiview.as_view(), name='department-create'),
    path('department/<str:id>/', DepartmentRetrieveApiView.as_view(), name='department-RUD'),
    path('departments/', DepartmentListApiView.as_view(), name='departments-List'),
    path('company-department/<str:id>/', CompanyDepartmentsListAPIView.as_view(), name='company-departments-List'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('', include(router.urls)),
]