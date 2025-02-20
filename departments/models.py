from django.db import models
from accounts.models import CustomUser
from company.models import company , AdminUser
from teams.models import CompaniesTeam
import uuid
from django.utils import timezone

class Departments(models.Model):
    id = models.UUIDField(default=uuid.uuid4 , primary_key=True , unique=True)
    name = models.CharField(max_length = 100)
    company = models.ForeignKey(company, on_delete=models.CASCADE, related_name='department_company')
    users = models.ManyToManyField(CompaniesTeam , blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    added_by = models.ForeignKey(CustomUser, models.CASCADE, default=None, null=True, related_name="department_added_by_main")
    is_active= models.BooleanField(default=True)
    
    
    REQUIRED_FIELDS = ['name']
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = ("Company Department")
        verbose_name_plural = ("Company Departments")

class DepartmentsDocuments(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True , unique=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    file = models.FileField(upload_to='media/documents/', null=True, blank=True)
    departments = models.ManyToManyField(Departments, related_name='document_departments', blank=True)
    assigned_users = models.ManyToManyField(CompaniesTeam, related_name='assigned_documents', blank=True)
    schedule_frequency = models.CharField(max_length=40,null=True,blank=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    added_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="document_departments_added_by", null=True, blank=True)
    is_active= models.BooleanField(default=True)


  # Naye fields frontend ke liye
    dueDate = models.DateField(null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    avgCompletionTime = models.IntegerField(null=True, blank=True)  # Minutes mein
    REQUIRED_FIELDS = ['name', 'file', 'departments']

 # ✅ Thumbnail Field Added
    thumbnail = models.ImageField(
    upload_to="public/static/thumbnails/",  # Corrected upload path
    default="thumbnails/default.png",  # Default path relative to STATICFILES_DIRS
    null=True,
    blank=True,
)
    def __str__(self):
        if self.name is not None:
            return self.name
        return "Data not found"
    
    def publish(self):
        if timezone.now() >= self.scheduled_time:
            self.published = True
            self.save()
    
    class Meta:
        verbose_name = ("Company Document")
        verbose_name_plural = ("Company Documents")