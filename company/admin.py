from django.contrib import admin
from .models import company, AdminUser
admin.site.register(company)
admin.site.register(AdminUser)
