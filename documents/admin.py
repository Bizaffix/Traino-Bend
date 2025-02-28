from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import UserDocuments, DocumentSummary, DocumentKeyPoints, DocumentQuiz, QuizQuestions, DocumentTeam, QuizResult, ScheduleDetail
from accounts.models import CompanyTeam, Departments
from django.utils.safestring import mark_safe
from django.utils.html import format_html
import json
from django import forms
from django.core.exceptions import ValidationError
from .forms import QuizQuestionsForm, DocumentForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.urls import path, reverse
from django.utils import timezone, dateformat
from django.conf import settings
from django.contrib import messages

def day_hour_format_converter(date_time_UTC):
    return dateformat.format(
        timezone.localtime(date_time_UTC),
        'm/d/Y H:i:s',
    )

def assignDocumentToUser(user, doc, department):
    try:
        das = DocumentTeam.objects.get(user_id = user.id, document_id = doc.id, department_id = department.id)
    except DocumentTeam.DoesNotExist:
        das = None


    if das is None:
        das = DocumentTeam(user_id = user.id, document_id = doc.id, department_id = department.id, is_assigned = False, notify_frequency = 0)
        das.save()    

class viewTeamView(PermissionRequiredMixin, DetailView):
    permission_required = "documents.view_userdocuments"
    template_name = "admin/documents/publish_document.html"
    model = UserDocuments
        

    def get_context_data(self, **kwargs):
        doc_team_ids = []
        try:
            # documents = UserDocuments.objects.filter(id = kwargs['object'].id)
            # for document in documents:
                departments = kwargs['object'].department.all().order_by('name')
                for dept in departments:
                    dept.team_users = DocumentTeam.objects.filter(document_id = kwargs['object'].id, department_id = dept.id ).order_by('user__email')
                    for t_user in dept.team_users:
                        doc_team_ids.append(str(t_user.id))
        except UserDocuments.DoesNotExist:
            departments = None
        doc_team_ids = ','.join(doc_team_ids)

        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
            "company_id": kwargs['object'].company,
            "departments": departments,
            "doc_team_ids": doc_team_ids
        }

class CustomDocumentAdmin(ModelAdmin):

    model = UserDocuments
    list_display = ('id', 'name', 'view_file', 'company', 'created_at', 'summary', 'key_points', 'quiz', 'assign_team', 'is_publish', 'updated','added_by')
    list_filter = [('published'), ('company', admin.RelatedOnlyFieldListFilter)]
    fieldsets = (
        (None, {'fields': ('name', 'file', 'company', 'department')}),
    )

    add_fieldsets = (
        (None, {'fields': ('name', 'file', 'company', 'department')}),
    )
    search_fields = ('name',)
    ordering = ('-id',)

    form = DocumentForm

    def get_urls(self):
        return [
            path(
                "<pk>/viewTeam/",
                self.admin_site.admin_view(viewTeamView.as_view()),
                name=f"documents_viewTeam",
            ),
            *super().get_urls(),
        ]

    def get_list_display(self, request):
        if request.user.role == 'User':
            self.list_display = ('id', 'name', 'view_file', 'company', 'created_at', 'summary', 'key_points', 'quiz', 'updated','added_by')
            
        else:
            self.list_display = ('id', 'name', 'view_file', 'company', 'created_at', 'summary', 'key_points', 'quiz', 'assign_team', 'is_publish', 'updated','added_by')
            
        return super().get_list_display(request)
    
    def get_list_filter(self, request):
        if request.user.role == 'User':
            self.list_filter = []
            
        else:
            self.list_filter = [('published'), ('company', admin.RelatedOnlyFieldListFilter)]
            
        return super().get_list_filter(request)

    def is_publish(self, obj):
        if obj.published:
            return format_html('<a href="javascript:;" onclick="javascript: togglePublishDocument({0}, this);" />Make Unpublish</a>', obj.id)
        else:
            return format_html('<a href="javascript:;" onclick="javascript: togglePublishDocument({0}, this);" />Make Publish</a>', obj.id)
    is_publish.short_description = 'Status'

    def assign_team(self, obj):
        url = reverse("admin:documents_viewTeam", args=[obj.pk])
        return format_html(f'<a href="{url}">View Team</a>')
    assign_team.short_description = 'Team'
    
    
    def updated(self, obj):
        if obj.updated_at:
            return day_hour_format_converter(obj.updated_at)
    updated.short_description = 'UPDATED AT'    
    
    
    def created_at(self, obj):
        if obj.created_date:
            return day_hour_format_converter(obj.created_date)
    
    def view_file(self, obj):
        if obj.file:
            return mark_safe('<a href="{0}" target="_blank" />View Document</a>'.format(obj.file.url))
        else:
            return '(No Document)'
    view_file.short_description = 'Document'

    def summary(self, obj):
        ds = DocumentSummary.objects.get(document=obj.id)
        url = reverse("admin:documents_documentsummary_change", args=[ds.id])
        return format_html(f'<a href="{url}">View Summary</a>')

    def key_points(self, obj):
        dkp = DocumentKeyPoints.objects.get(document=obj.id)
        url = reverse("admin:documents_documentkeypoints_change", args=[dkp.id])
        return format_html(f'<a href="{url}">View Keypoints</a>')
 
    def quiz(self, obj):
        dq = DocumentQuiz.objects.get(document=obj.id)
        url = reverse("admin:documents_documentquiz_change", args=[dq.id])
        return format_html(f'<a href="{url}">View Quiz</a>')

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        cur_user = request.user
        cur_user_id = request.user.id

        if obj.id is None:
            obj.added_by = request.user
        elif obj.added_by is None:    
            obj.added_by = request.user

        obj.save()
        
        document_departments = request.POST.getlist('department')
        for dept_id in document_departments:
            doc_dept = Departments.objects.get(id=dept_id)
            team_users = CompanyTeam.objects.filter(company_id = obj.company_id, department_id = doc_dept.id ).order_by('first_name')
            for team_user in team_users:
                assignDocumentToUser(team_user, obj, doc_dept)

        try:
            dq = DocumentQuiz.objects.get(document_id=obj.id)
        except DocumentQuiz.DoesNotExist:
            dq = None
        
        try:
            ds = DocumentSummary.objects.get(document_id=obj.id)
        except DocumentSummary.DoesNotExist:
            ds = None
        
        try:
            dkp = DocumentKeyPoints.objects.get(document_id=obj.id)
        except DocumentKeyPoints.DoesNotExist:
            dkp = None

        if dq is None:
            dq = DocumentQuiz(name=str(obj.name), prompt_text='25 multiple choice questions', company_id = int(obj.company_id), content='', document_id= str(obj.id), added_by_id= str(cur_user_id))
            # dq = DocumentQuiz(name=str(obj.name), prompt_text='25 multiple choice questions', company = cur_user, content='', document_id= str(obj.id))
            dq.save()
        if ds is None:
            ds = DocumentSummary(content='', prompt_text='concise summary', company_id = int(obj.company_id), document_id= str(obj.id), added_by_id= str(cur_user_id))
            ds.save()
        if dkp is None:
            dkp = DocumentKeyPoints(content='', prompt_text='concise outline in numeric order list', company_id = int(obj.company_id), document_id= str(obj.id), added_by_id= str(cur_user_id))
            dkp.save()
    # def has_delete_permission(self, request, obj=None):
    #     return False

    # def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
    #     extra_context = extra_context or {}
    #     extra_context['show_save_and_continue'] = False    
    #     extra_context['show_save_and_add_another'] = False    

    #     return super().changeform_view(request, object_id, form_url, extra_context=extra_context)

# class DocumentSummaryAdmin(ModelAdmin):

#     model = DocumentSummary
#     list_display = ('id' , 'document', 'summary')
#     list_filter = ('document',)
#     search_fields = ('document','summary')
#     readonly_fields = ('id',)

    
#     fieldsets = (
#         (None, {'fields': ('document', 'summary')}),
#     )

#     def get_list_display(self, request):
#         if request.user.role == 'Admin':
#             self.list_display = ('document', )
#         else:
#             self.list_display = ('id', 'document', 'summary')
#         return super().get_list_display(request)

#     def get_fieldsets(self, request, obj=None):
#         if request.user.role == 'Admin':
#             self.fieldsets = (
#                 (None, {'fields': ('summary',)}),
#             )
#         else:
#             self.fieldsets = (
#                 (None, {'fields': ('document', 'summary')}),
#             )
#         return super().get_fieldsets(request, obj)

#     def render_change_form(self, request, context, *args, **kwargs):
#         """We need to update the context to show the button."""
        
#         if request.user.role == 'Admin':
#             context.update({'show_generate_button': False})  
#         else:
#             context.update({'show_generate_button': True})  

#         return super().render_change_form(request, context, *args, **kwargs)


#     def has_delete_permission(self, request, obj=None):
#         return False
#     def has_add_permission(self, request, obj=None):
#         return False

class DocumentKeyPointsAdmin(ModelAdmin):

    model = DocumentKeyPoints
    list_display = ('id','keypoints','document')
    list_filter = ('id','keypoints','document')
    search_fields = ('id','keypoints','document')
    
    fieldsets = (
        (None, {'fields': ('keypoints','document')}),
    )

    def get_list_display(self, request):
        if request.user.role == 'Admin':
            self.list_display = ('id','keypoints','document')
        else:
            self.list_display = ('id','keypoints','document')
        return super().get_list_display(request)

    def get_fieldsets(self, request, obj=None):
        if request.user.role == 'Admin':
            self.fieldsets = (
                (None, {'fields': ('keypoints',)}),
            )
        else:
            self.fieldsets = (
                (None, {'fields': ('id','keypoints','document')}),
            )
        return super().get_fieldsets(request, obj)

    def render_change_form(self, request, context, *args, **kwargs):
        """We need to update the context to show the button."""
        
        if request.user.role == 'Admin':
            context.update({'show_generate_button': False})  
        else:
            context.update({'show_generate_button': True})  

        return super().render_change_form(request, context, *args, **kwargs)


    def has_delete_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False

class QuizQuestionsInline(admin.TabularInline):
    model = QuizQuestions
    readonly_fields = ('id',)
    extra = 0
    can_delete = False
    show_change_link = False
    # classes = ('collapse', )
    form = QuizQuestionsForm

    @property
    def media(self):
        media = super(QuizQuestionsInline, self).media

        # media._css_lists(css)
        media._js_lists[0].pop()
        media._js_lists[0].append("/media/js/inlines.js")
        return media


    template = 'admin/edit_inline/documents/quizquestions/tabular.html'

    def has_add_permission(self, request, obj):
        return True
    
    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

class QuizResultView(PermissionRequiredMixin, DetailView):
    permission_required = "documents.view_documentquiz"
    template_name = "admin/documents/documentquiz/quiz_result.html"
    model = DocumentQuiz
    

    def get_context_data(self, **kwargs):
        
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
        }

class AttemptQuizView(PermissionRequiredMixin, DetailView):
    permission_required = "documents.view_documentquiz"
    template_name = "admin/documents/documentquiz/attempt_quiz.html"
    model = DocumentQuiz
        

    def get_context_data(self, **kwargs):
        try:
            dquiz = QuizQuestions.objects.filter(quiz = kwargs['object'].id)
        except QuizQuestions.DoesNotExist:
            dquiz = None
        quiz_ids = []
        for quiz in dquiz:
            quiz_ids.append(str(quiz.id))
        quiz_ids = ','.join(quiz_ids)

        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": self.model._meta,
            "quiz_questions": dquiz,
            "question_ids": quiz_ids
        }

class DocumentQuizAdmin(ModelAdmin):
    
    model = DocumentQuiz
    # form = QuizQuestionsForm
    list_display = ('name', 'prompt_text', 'document')
    list_filter = ('document',)
    search_fields = ('prompt_text','content', 'name')
    

    inlines = [QuizQuestionsInline]

    

    def get_urls(self):
        return [
            path(
                "<pk>/attemptQuiz",
                self.admin_site.admin_view(AttemptQuizView.as_view()),
                name=f"documents_documentquiz_attemptQuiz",
            ),
            path(
                "<pk>/quizResult",
                self.admin_site.admin_view(QuizResultView.as_view()),
                name=f"documents_documentquiz_quizResult",
            ),
            *super().get_urls(),
        ]

    def get_list_display(self, request):
        if request.user.role == 'User':
            self.list_display = ('name', 'document')
            
        else:
            self.list_display = ('name', 'prompt_text', 'document')
            
        return super().get_list_display(request)

    def get_fieldsets(self, request, obj=None):
        if request.user.role == 'User':
            self.fieldsets = (
                (None, {'fields': ()}),
            )
        else:
            self.fieldsets = (
                (None, {'fields': ('name', 'content', 'prompt_text')}),
            )
        return super().get_fieldsets(request, obj)
    

    def render_change_form(self, request, context, *args, **kwargs):
        """We need to update the context to show the button."""
        # try:
        #     dquiz = QuizQuestions.objects.filter(quiz = kwargs['obj'].id)
        # except QuizQuestions.DoesNotExist:
        #     dquiz = None
        # quid_ids = []
        # for quiz in dquiz:
        #     quid_ids.append(str(quiz.id))
        # quid_ids = ','.join(quid_ids)

        # context.update({'quiz_questions': dquiz})
        # context.update({'question_ids': quid_ids})

        if request.user.role == 'User':
            context.update({'show_generate_button': False})
            context.update({'show_answers': False})
            context.update({'save_buttons_on_top': True})
            context.update({'show_attempt_quiz': True})
            
        else:
            context.update({'show_generate_button': True})
            context.update({'show_answers': True})
            context.update({'save_buttons_on_top': False})
            context.update({'show_attempt_quiz': False})

        return super().render_change_form(request, context, *args, **kwargs)
    
    
    def has_delete_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False
    
    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        # print("reques is")
        # print(request)  
        # print("object is")
        # print(obj)
        
        obj.save()
        
        try:
            dquiz = QuizQuestions.objects.filter(quiz_id=obj.id)
        except QuizQuestions.DoesNotExist:
            dquiz = None
        if (dquiz is None or len(dquiz) == 0) and obj.content is not None and obj.content != '':
            print("adding quiz")
            document_quiz = json.loads(obj.content)
            for quiz in document_quiz:
                if quiz['question'] is not None and quiz['options'] is not None and quiz['answer'] is not None:
                    q_question = QuizQuestions(question = quiz['question'], option_1 = quiz['options'][0], option_2 = quiz['options'][1], option_3 = quiz['options'][2], option_4 = quiz['options'][3], answer = quiz['answer'], quiz_id = str(obj.id), document_id = str(obj.document_id))
                    q_question.save()
        else:
            print("quiz already there")
            # print(len(dquiz))
    
class ScheduleDetailAdmin(admin.ModelAdmin):
    # Specify which fields to display in the list view
    list_display = ('id', 'quiz_id', 'question_id', 'user_id', 'document_id', 'created_at', 'updated_at')
    
    # Add filters for the list view
    list_filter = ('quiz_id', 'question_id', 'user_id', 'document_id')
    
    # Add search functionality
    search_fields = ('quiz_id', 'question_id', 'user_id', 'document_id')
    
    # Set up how fields should be grouped in the admin form
    fieldsets = (
        (None, {'fields': ('quiz_id', 'question_id', 'user_id', 'document_id')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    # Make timestamps read-only
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(ScheduleDetail, ScheduleDetailAdmin)
admin.site.register(UserDocuments, CustomDocumentAdmin)
admin.site.register(DocumentSummary)
admin.site.register(DocumentKeyPoints)#, DocumentKeyPointsAdmin
admin.site.register(DocumentQuiz)
admin.site.register(QuizQuestions)
admin.site.register(QuizResult)

# Register your models here.
