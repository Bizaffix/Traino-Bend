from django.db import models
from accounts.models import CustomUser, Departments
from company.models import AdminUser
import uuid


class UserDocuments(models.Model):
    id = models.BigAutoField(primary_key = True)
    name = models.CharField(max_length = 100, null=True)
    file = models.FileField(upload_to='documents/', null=True , blank=True)
    company = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='document_company')
    department = models.ManyToManyField(Departments, related_name='document_departments')
    published = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    added_by = models.ForeignKey(CustomUser, models.CASCADE, default=None, null=True, related_name="document_added_by")

    REQUIRED_FIELDS = ['name', 'file', 'department']

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = ("Company Document")
        verbose_name_plural = ("Company Documents")

class DocumentTeam(models.Model):
    id = models.BigAutoField(primary_key= True)
    document = models.ForeignKey(UserDocuments, on_delete=models.CASCADE, related_name='assignee_document', default=0)
    # company = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assignee_company', default=0)
    department = models.ForeignKey(Departments, on_delete=models.CASCADE, related_name='assignee_department', default=0)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assignee_user', default=0)
    is_assigned = models.BooleanField(default=False)
    notify_frequency =models.CharField(max_length = 2, default = '0')

from company.models import company
from departments.models import DepartmentsDocuments

class DocumentSummary(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True , unique=True)
    summary = models.TextField(blank=True, null=True)
    prompt = models.TextField(blank=True, null=True)
    document = models.ForeignKey(DepartmentsDocuments, on_delete=models.CASCADE, related_name='summary_document')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    added_by = models.ForeignKey(CustomUser, models.CASCADE, default=None, null=True, related_name="summary_added_by")
    # is_active= models.BooleanField(default=True)

    REQUIRED_FIELDS = ['summary', 'document']

    def __str__(self):
        if self.document.name is not None:
            return self.document.name
        return "Failed To load Name"
    class Meta:
        verbose_name = ("Summary")
        verbose_name_plural = ("Summary")
    
class DocumentKeyPoints(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    keypoints = models.TextField(blank=True, null=True)
    prompt = models.TextField(blank=True, null=True)
    document = models.ForeignKey(DepartmentsDocuments, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    added_by = models.ForeignKey(CustomUser, models.CASCADE, default=None, null=True, related_name="keypoint_added_by")
    # is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.document.name is not None:
            return self.document.name
        return "Failed To load Name"
    class Meta:
        verbose_name = ("Keypoints")
        verbose_name_plural = ("Keypoints")

class DocumentQuiz(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    name = models.CharField(max_length = 255)
    quiz = models.TextField(blank=True, null=True)
    prompt = models.TextField(blank=True, null=True)
    document = models.ForeignKey(DepartmentsDocuments, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    upload = models.BooleanField(default=False)
    added_by = models.ForeignKey(CustomUser, models.CASCADE, default=None, null=True, related_name="quiz_added_by")
    
    def __str__(self):
        return self.name
    
    def delete_quiz(self):
        self.delete()
        
    class Meta:
        verbose_name = ("Quiz")
        verbose_name_plural = ("Quizes")

class QuizQuestions(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    question = models.CharField(max_length = 255, blank=True, null=True)
    option_1 = models.CharField(max_length = 255, blank=True, null=True)
    option_2 = models.CharField(max_length = 255, blank=True, null=True)
    option_3 = models.CharField(max_length = 255, blank=True, null=True)
    option_4 = models.CharField(max_length = 255, blank=True, null=True)    
    answer = models.CharField(max_length = 2, blank=True, null=True)
    quiz = models.ForeignKey(DocumentQuiz, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    added_by = models.ForeignKey(CustomUser, models.CASCADE, default=None, null=True, related_name="quiz_question_added_by")
    
    def __str__(self):
        return self.question
    
    class Meta:
        verbose_name = ("Question")
        verbose_name_plural = ("Questions")


from teams.models import CompaniesTeam

class QuizResult(models.Model):
    user = models.ForeignKey(CompaniesTeam , on_delete=models.CASCADE)
    quiz = models.ForeignKey(DocumentQuiz, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=10)

    class Meta:
        unique_together = ('user', 'quiz')

    def __str__(self):
        return f"{self.user.members.first_name} - {self.quiz.name} - {self.status}"
        
class SummaryCount(models.Model):
    admin = models.ForeignKey(AdminUser , null=True , blank=True , on_delete=models.CASCADE)
    document = models.ForeignKey(DepartmentsDocuments, on_delete=models.CASCADE)
    request_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.admin.admin.first_name} has summary count {self.request_count} for {self.document}"
    
class KeypointsCount(models.Model):
    admin = models.ForeignKey(AdminUser , null=True , blank=True, on_delete=models.CASCADE)
    document = models.ForeignKey(DepartmentsDocuments, on_delete=models.CASCADE)
    request_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.admin.admin.first_name} has summary count {self.request_count} for {self.document}"

class ScheduleDetail(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    quiz_id = models.UUIDField()
    question_id = models.UUIDField()
    user_id = models.UUIDField()
    document_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
