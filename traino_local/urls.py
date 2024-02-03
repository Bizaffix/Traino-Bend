"""
URL configuration for traino_local project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from documents.views import generateDocumentSummary, generateDocumentKeypoints, generateDocumentQuiz, attemptQuiz, saveDocumentTeam, publishDocument
from accounts.views import DepartmentAutocompleteView, CompanyAutocompleteView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('generateDocumentSummary/', generateDocumentSummary),
    path('generateDocumentKeypoints/', generateDocumentKeypoints),
    path('generateDocumentQuiz/', generateDocumentQuiz),
    path('attemptQuiz/<int:quiz_id>', attemptQuiz),
    path('saveDocumentTeam/<int:document_id>', saveDocumentTeam),
    path('publishDocument/', publishDocument),
    path('department_autocomplete/', DepartmentAutocompleteView.as_view(), name='department_autocomplete'),
    path('company_autocomplete/', CompanyAutocompleteView.as_view(), name='company_autocomplete'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()

admin.site.site_header = "TRAINO.AI Admin"
admin.site.site_title = "TRAINO.AI Admin Portal"
admin.site.index_title = "Welcome to TRAINO.AI"