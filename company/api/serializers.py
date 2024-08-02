from company.models import company , AdminUser
from rest_framework import serializers
from teams.models import CompaniesTeam
from departments.models import Departments
from api.serializers import DepartmentSerializers
from teams.api.serializers import CompaniesTeamDetailsSerializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.core.mail import send_mail
import random
import string
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from accounts.models import CustomUser


class AdminSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    company = serializers.PrimaryKeyRelatedField(queryset=company.objects.all(), write_only=True)
    update_key = serializers.SerializerMethodField(read_only=True)
    update_url = serializers.SerializerMethodField(read_only=True)
    first_name = serializers.SerializerMethodField(read_only=True)
    last_name = serializers.SerializerMethodField(read_only=True)
    # company = serializers.SerializerMethodField(read_only=True)
    phone = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = AdminUser
        fields = ['id' , 'update_key', 'update_url' , 'admin' , 'company' , 'email' , 'first_name' , 'last_name' ,'phone', 'is_active']

    def create(self, validated_data):
        email = validated_data.pop('email')
        company = validated_data.pop('company')
        
        
        try:
            admin = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        # # Check if an admin with the same email exists in the same company
        if AdminUser.objects.filter(admin=admin, company=company).exists():
            raise serializers.ValidationError("Admin with this email already exists in this company.")

        # Check if the admin is already associated with another company
        if AdminUser.objects.filter(admin=admin).exclude(company=company).exists():
            raise serializers.ValidationError("Admin is already associated with this or some another company.")

        # Create the admin user
        admin_user = AdminUser.objects.create(admin=admin , company=company ,**validated_data)
        return admin_user
        
#         send_mail(
#             subject="Welcome to Traino-ai",
#             message=f'''Welcome to Traino-ai.

# We're so excited to be working with you, and we want to be sure we start off on the right foot.
# Your email and password to access the Traino-ai portal is shown below.Please click below to sign-in.

# Username: {admin_user.admin.email}
# Password: {temp_password}
# Role: {admin_user.admin.role}

# Please <a href="{login_url}">Log in</a> and complete your profile.

# Regards
# Traino-ai.''',
#             from_email="no-reply@traino.ai",
#             recipient_list=[admin_user.admin.email],
#             fail_silently=False,
#         )
    
    def get_phone(self , obj):
        return str(obj.admin.phone)
    
    def get_update_url(self , obj):
        return f"https://127.0.0.1:8000/api/update-account/{obj.admin.id}"
    
    
    def get_update_key(self , obj):
        return obj.admin.id
    
    def get_first_name(self , obj):
        return obj.admin.first_name
    
    def get_last_name(self , obj):
        return obj.admin.last_name
    
    def get_company(self , obj):
        return obj.company.name

    # def get_admin(self, obj):
    #     return obj.id   
class AdminUpdateDeleteSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField(read_only=True)
    first_name = serializers.SerializerMethodField(read_only=True)
    role = serializers.SerializerMethodField(read_only=True)
    id = serializers.SerializerMethodField(read_only=True)
    last_name = serializers.SerializerMethodField(read_only=True)
    company = serializers.SerializerMethodField(read_only=True)
    phone = serializers.SerializerMethodField(read_only=True)
    password = serializers.SerializerMethodField(read_only=True)
    admin_update_key = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = AdminUser
        fields = ['id' , 'first_name' , 'last_name', 'email' , 'role' , 'phone' , 'password' , 'company' , 'admin_update_key']

    def get_id(self, obj):
        return obj.id
    
    def get_email(self , obj):
        return obj.admin.email


    def get_role(self , obj):
        return obj.admin.role

    def get_first_name(self, obj):
        return obj.admin.first_name
    
    
    def get_password(self, obj):
        return obj.admin.password
    
    
    def get_phone(self, obj):
        return str(obj.admin.phone)
    
    def get_last_name(self, obj):
        return obj.admin.last_name

    def get_company(self , obj):
        return obj.company.name
    
    def get_admin_update_key(self, obj):
        return obj.admin.id
    
class CompanySerializer(serializers.ModelSerializer):
    # departments = serializers.SerializerMethodField(read_only=True)
    # admin = serializers.SerializerMethodField(read_only=True)
    id = serializers.SerializerMethodField(read_only=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    class Meta:
        model = company
        fields = '__all__'
        
    def get_id(self , obj):
        return obj.id
    
    # def get_admin(self, obj):
    #     admins = AdminUser.objects.prefetch_related('company').filter(company=obj, is_active=True)
    #     serializer = AdminSerializer(admins, many=True)
    #     return serializer.data
    
    # def get_departments(self, obj):
    #     admins = Departments.objects.prefetch_related('company').filter(company=obj)
    #     serializer = DepartmentSerializers(admins, many=True)
    #     return serializer.data
    
    
class CompaniesListSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    class Meta:
        model = company
        fields = ['id','name', 'logo']
        
    def get_logo(self , obj):
        if obj.logo:
            return self.context['request'].build_absolute_uri(obj.logo.url)
        return None