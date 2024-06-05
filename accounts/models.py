from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from django.contrib.admin import AdminSite
from phonenumber_field.modelfields import PhoneNumberField
original_get_app_list = AdminSite.get_app_list
import uuid 

class CustomUser(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4 , primary_key=True,unique=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    username = None
    email = models.EmailField(('email address'), unique=True)
    phone = PhoneNumberField(null=True, blank=True)
    role =models.CharField(max_length=20, choices=( ('Super Admin', 'Super Admin'), ('Admin', 'Admin'), ('User', 'User') ), default='Super Admin' )
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    added_by = models.ForeignKey("self", models.CASCADE, default=None, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = ("Super Admin")
        verbose_name_plural = ("Super Admins")

class Departments(models.Model):
    id = models.BigAutoField(primary_key = True)
    name = models.CharField(max_length = 100)
    company = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='department_company')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    added_by = models.ForeignKey(CustomUser, models.CASCADE, default=None, null=True, related_name="department_added_by")
    
    REQUIRED_FIELDS = ['name']
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = ("Company Department")
        verbose_name_plural = ("Company Departments")

class CompanyTeam(CustomUser):
    # company_team_id = models.BigAutoField(primary_key = True)
    company = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='team_company')
    # team_member = models.ForeignKey(CustomUser , on_delete=models.CASCADE , related_name='team_member')
    department = models.ForeignKey(Departments, on_delete=models.CASCADE, related_name='team_department')
    CustomUser.role = 'User'

    REQUIRED_FIELDS = ['first_name', 'last_name', 'role', 'company', 'department']

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = ("Company Team")
        verbose_name_plural = ("Company Teams")

class CustomCompanyUser(CustomUser):
    CustomUser.role = 'Admin'
    #objects = AdminUserTypeManager()
    class Meta:
        proxy = True
        verbose_name = ("Company Admin")
        verbose_name_plural = ("Company Admins")

class CustomCompanyTeamUser(CustomUser):
    CustomUser.role = 'User'
    #objects = AdminUserTypeManager()
    class Meta:
        proxy = True
        verbose_name = ("Company User")
        verbose_name_plural = ("Company Users")


class MyAdminSite(AdminSite):
    
    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        ordering = {
            "Super Admins": 1,
            "Company Admins": 2,
            "Company Departments": 3,
            "Company Teams": 4,
            "Company Documents": 5,
            "Summary": 6,
            "Keypoints": 7,
            "Quizes": 8,
            "Companys":9,
            "Company Team Members":10,
            "Company Users":11,
            "Questions":12,
        }

        app_dict = self._build_app_dict(request, app_label)

        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())
        
        # app_list = original_get_app_list(self, request)

        # Sort the models custom within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: ordering[x['name']])

        return app_list

AdminSite.get_app_list = MyAdminSite.get_app_list