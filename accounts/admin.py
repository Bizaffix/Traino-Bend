from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'role',)
    list_filter = ('is_active', 'role',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name', 'last_name')}),
        ('Permissions', {'fields' : ('is_active', 'role')}),
        ('History', {'fields' : ('date_joined', 'last_login')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name')}
        ),
        ('Permissions', {'fields' : ('is_active', 'role')}),
        ('History', {'fields' : ('date_joined', 'last_login')}),
    )
    search_fields = ('email', 'first_name', 'last_name',)
    ordering = ('email', 'first_name', 'last_name',)

    # def custom_role(self, obj):
    #     result = obj
    #     if result.is_staff == True and result.is_superuser == True:
    #         custom_role_name = 'Super Admin'
    #     else:
    #         custom_role_name = 'Admin'
    #     return custom_role_name
    # custom_role.short_description = 'Role'

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        if obj.role == 'Super Admin':
            obj.is_staff = True
            obj.is_superuser = True
            # permission = Permission.objects.get(name='Can view user')
            # print(permission)
            # obj.user_permissions.add(permission)
        else:
            obj.is_staff = True
            obj.is_superuser = False
            
            # permissions = Permission.objects.filter(codename__in=('view_userdocuments', 'view_documentsummary', 'view_documentkeypoints', 'view_documentquiz', 'view_quizquestions'))
            # obj.user_permissions.add(*permissions)

            

        obj.save()

        permissions = Permission.objects.filter(pk__in =(28,32,36,40,44))
        obj.user_permissions.add(*permissions)
        # user_permission = user_permissions.get(permission_id=28)
        # print(permissions)

    ##def role_filter(self, obj):
        
        ##return CustomUser.objects.filter(is_superuser == True)
    ##is_superuser.short_description = 'Role'
    

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.unregister(Group)
#admin.site.register(AdminUserType, CustomUserAdmin)

# Register your models here.
