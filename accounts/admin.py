from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import ModelAdmin
from .models import CustomUser, CustomCompanyUser, CompanyTeam, Departments
from .forms import CustomUserCreationForm, CustomUserChangeForm, CompanyTeamCreationForm, CompanyTeamChangeForm, CompanyUserCreationForm, CompanyUserChangeForm, DepartmentForm
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group
from django.utils import timezone, dateformat


def day_hour_format_converter(date_time_UTC):
    return dateformat.format(
        timezone.localtime(date_time_UTC),
        'm/d/Y H:i:s',
    )

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    model = CustomUser
    list_display = ('id', 'email', 'first_name', 'last_name', 'is_active', 'role', 'created','updated','added_by',)
    list_filter = ('is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name', 'last_name')}),
        ('Permissions', {'fields' : ('is_active',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name')}
        ),
        ('Permissions', {'fields' : ('is_active',)}),
    )
    search_fields = ('email', 'first_name', 'last_name',)
    ordering = ('-id',)

    def updated(self, obj):
        if obj.updated_at:
            return day_hour_format_converter(obj.updated_at)
    updated.short_description = 'UPDATED AT' 

    def created(self, obj):
        if obj.created_at:
            return day_hour_format_converter(obj.created_at)
    created.short_description = 'CREATED AT' 

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

        if obj.id is None:
            obj.added_by = request.user
        elif obj.added_by is None:    
            obj.added_by = request.user

        obj.save()

        permissions = Permission.objects.filter(pk__in =(28,32,36,40,44))
        obj.user_permissions.add(*permissions)
        # user_permission = user_permissions.get(permission_id=28)
        # print(permissions)

    # default backend filter for list display
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # if request.user.is_superuser:
        #     return qs
        #return qs.filter(author=request.user)
        return qs.filter(is_superuser=True)
    
    ##def role_filter(self, obj):
        
        ##return CustomUser.objects.filter(is_superuser == True)
    ##is_superuser.short_description = 'Role'
    

class CustomCompanyAdmin(UserAdmin):
    add_form = CompanyUserCreationForm
    form = CompanyUserChangeForm

    model = CustomCompanyUser
    list_display = ('id','email', 'first_name', 'last_name', 'is_active', 'role', 'created','updated','added_by',)
    list_filter = ('is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name', 'last_name')}),
        ('Permissions', {'fields' : ('is_active',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name')}
        ),
        ('Permissions', {'fields' : ('is_active',)}),
    )
    search_fields = ('email', 'first_name', 'last_name',)
    ordering = ('-id',)

    def updated(self, obj):
        if obj.updated_at:
            return day_hour_format_converter(obj.updated_at)
    updated.short_description = 'UPDATED AT' 

    def created(self, obj):
        if obj.created_at:
            return day_hour_format_converter(obj.created_at)
    created.short_description = 'CREATED AT' 


    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        
        obj.is_staff = True
        obj.is_superuser = False
        obj.role = 'Admin'

        if obj.id is None:
            obj.added_by = request.user
        elif obj.added_by is None:    
            obj.added_by = request.user

        obj.save()

        permissions = Permission.objects.filter(pk__in =(28,32,36,40,44))
        obj.user_permissions.add(*permissions)
        
    # default backend filter for list display
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # if request.user.is_superuser:
        #     return qs
        #return qs.filter(author=request.user)
        return qs.filter(is_superuser=False, role='Admin')

class CompanyTeamAdmin(UserAdmin):
    add_form = CompanyTeamCreationForm
    form = CompanyTeamChangeForm

    model = CompanyTeam
    list_display = ('id','email', 'first_name', 'last_name', 'is_active', 'company', 'department', 'role', 'created','updated','added_by',)
    list_filter = [('is_active'),('company', admin.RelatedOnlyFieldListFilter)]
    fieldsets = (
        (None, {'fields': ('email', 'password', 'first_name', 'last_name', 'company', 'department')}),
        ('Permissions', {'fields' : ('is_active',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'company', 'department')}
        ),
        ('Permissions', {'fields' : ('is_active',)}),
    )
    search_fields = ('email', 'first_name', 'last_name','department__name',)
    ordering = ('-id',)

    def updated(self, obj):
        if obj.updated_at:
            return day_hour_format_converter(obj.updated_at)
    updated.short_description = 'UPDATED AT' 

    def created(self, obj):
        if obj.created_at:
            return day_hour_format_converter(obj.created_at)
    created.short_description = 'CREATED AT' 

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "company":
            kwargs["queryset"] = CustomUser.objects.filter(role='Admin')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        
        obj.is_staff = True
        obj.is_superuser = False
        obj.role = 'User'

        if obj.id is None:
            obj.added_by = request.user
        elif obj.added_by is None:    
            obj.added_by = request.user

        obj.save()

        permissions = Permission.objects.filter(pk__in =(32,36,40,44,48,52))
        obj.user_permissions.add(*permissions)
        obj.user_permissions.remove(28)
        
    # default backend filter for list display
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_superuser=False, role='User')

class CompanyDepartmentAdmin(ModelAdmin):

    model = Departments
    list_display = ('id','name', 'company', 'created','updated','added_by',)
    list_filter = [('company', admin.RelatedOnlyFieldListFilter)]
    fieldsets = (
        (None, {'fields': ('name', 'company')}),
    )

    form = DepartmentForm

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'company')}
        ),
    )
    search_fields = ('name',)
    ordering = ('-id',)

    def updated(self, obj):
        if obj.updated_at:
            return day_hour_format_converter(obj.updated_at)
    updated.short_description = 'UPDATED AT' 

    def created(self, obj):
        if obj.created_at:
            return day_hour_format_converter(obj.created_at)
    created.short_description = 'CREATED AT' 

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "company":
            kwargs["queryset"] = CustomUser.objects.filter(role='Admin')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        
        if obj.id is None:
            obj.added_by = request.user
        elif obj.added_by is None:    
            obj.added_by = request.user

        obj.save()

# Register your models here.
            
admin.site.register(CustomUser, CustomUserAdmin,)
admin.site.unregister(Group)
admin.site.register(CustomCompanyUser, CustomCompanyAdmin)
admin.site.register(CompanyTeam, CompanyTeamAdmin)
admin.site.register(Departments, CompanyDepartmentAdmin)