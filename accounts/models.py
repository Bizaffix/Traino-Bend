from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(('email address'), unique=True)
    role =models.CharField(max_length=20, choices=( ('Super Admin', 'Super Admin'), ('Admin', 'Admin') ), default='Super Admin' )


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    # class Meta:
    #     verbose_name = ("Super Admin")
    #     verbose_name_plural = ("Super Admins")
    

# class AdminUserType(CustomUser):
#     CustomUser.role = 'Admin'
#     #objects = AdminUserTypeManager()
#     class Meta:
#         proxy = True
#         verbose_name = ("Admin")
#         verbose_name_plural = ("Admins")