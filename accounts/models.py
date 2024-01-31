from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from django.contrib.admin import AdminSite
original_get_app_list = AdminSite.get_app_list


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(('email address'), unique=True)
    role =models.CharField(max_length=20, choices=( ('Super Admin', 'Super Admin'), ('Admin', 'Admin'), ('User', 'User') ), default='Super Admin' )
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    added_by = models.ForeignKey("self", models.CASCADE, default=None, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = ("Super Admin")
        verbose_name_plural = ("Super Admins")

class Departments(models.Model):
    id = models.BigAutoField(primary_key = True)
    name = models.CharField(max_length = 100)
    company = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='department_company', default=0)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    added_by = models.ForeignKey(CustomUser, models.CASCADE, default=None, null=True, related_name="department_added_by")
    

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = ("Company Department")
        verbose_name_plural = ("Company Departments")

class CompanyTeam(CustomUser):
    company_team_id = models.BigAutoField(primary_key = True)
    company = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='team_company', default=0)
    department = models.ForeignKey(Departments, on_delete=models.CASCADE, related_name='team_department', default=None)
    CustomUser.role = 'User'

    REQUIRED_FIELDS = []

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

class MyAdminSite(AdminSite):
    
    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        ordering = {
            "Super Admins": 1,
            "Company Admins": 2,
            "Company Departments": 3,
            "Company Teams": 4,
            "Documents": 5,
            "Summary": 6,
            "Keypoints": 7,
            "Quizes": 8,
        }
        
        app_list = original_get_app_list(self, request)

        # Sort the models custom within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: ordering[x['name']])

        return app_list

AdminSite.get_app_list = MyAdminSite.get_app_list