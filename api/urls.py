from django.urls import path, include
from api import views
from rest_framework.routers import DefaultRouter
from djoser.views import UserViewSet
from .views import (DepartmentCreateApiview,
                    CreateSummaryApiView,
                    CreateKeypointsApiView,
                    DepartmentListApiView,
                    DepartmentRetrieveApiView, 
                    CompanyDepartmentsListAPIView, 
                    AddUserToDepartmentView,
                    CreateQuizessApiView,
                    SubmitQuizView,
                    UploadQuiz,
                    EditQuizes,
                    QuestionsofQuiz,
                    DeleteQuizApiView)

router = DefaultRouter()

router.register('myTeams', views.CompanyTeamModelViewSet, basename="company_team_api")
# router.register('myLearnings', views.DocumentModelViewSet, basename="company_document_api")
# router.register('summary', views.DocumentSummaryModelViewSet, basename="company_document_summary_api")
# router.register('keypoints', views.DocumentKeyPointsModelViewSet, basename="company_document_keypoints_api")

urlpatterns = [
    path('asign-user-department/', AddUserToDepartmentView.as_view(), name='add_user_to_department'),
    path('create-department/', DepartmentCreateApiview.as_view(), name='department-create'),
    path('summary/', CreateSummaryApiView.as_view() , name='create-summary'),
    path('quiz/submit/', SubmitQuizView.as_view(), name='submit_quiz'),
    path('keypoints/', CreateKeypointsApiView.as_view() , name='create-keypoints'),
    path('quiz/upload/' ,UploadQuiz.as_view() , name="uploadQuiz"),
    path('question/<uuid:question_id>/' ,EditQuizes.as_view() , name="EditQuestion"),
    path('quiz/', CreateQuizessApiView.as_view() , name='create-quiz'),
    path("quiz/<str:quiz_id>/" , CreateQuizessApiView.as_view() , name='delete_quiz'),
    path('questions/', QuestionsofQuiz.as_view() , name='questions-of-quiz'),
    path('department/<str:id>/', DepartmentRetrieveApiView.as_view(), name='department-RUD'),
    path('departments/', DepartmentListApiView.as_view(), name='departments-List'),
    path('company-department/<str:id>/', CompanyDepartmentsListAPIView.as_view(), name='company-departments-List'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('', include(router.urls)),
]