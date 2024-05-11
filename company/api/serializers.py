from company.models import company , AdminUser
from rest_framework import serializers
from teams.models import CompaniesTeam
from departments.models import Departments
from api.serializers import DepartmentSerializers
from teams.api.serializers import CompaniesTeamDetailsSerializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

class AdminSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField(read_only=True)
    update_key = serializers.SerializerMethodField(read_only=True)
    update_url = serializers.SerializerMethodField(read_only=True)
    first_name = serializers.SerializerMethodField(read_only=True)
    last_name = serializers.SerializerMethodField(read_only=True)
    company = serializers.SerializerMethodField(read_only=True)
    phone = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = AdminUser
        fields = ['id' , 'update_key', 'update_url' , 'company' , 'email' , 'first_name' , 'last_name' ,'phone', 'is_active']
        
    def create(self, validated_data):
        email = validated_data.get('admin')
        company = validated_data.get('company')
        
        # # Check if an admin with the same email exists in the same company
        if AdminUser.objects.filter(admin=email, company=company).exists():
            raise serializers.ValidationError("Admin with this email already exists in this company.")

        # Check if the admin is already associated with another company
        if AdminUser.objects.filter(admin=email).exclude(company=company).exists():
            raise serializers.ValidationError("Admin is already associated with this or some another company.")

        # Create the admin user
        admin_user = AdminUser.objects.create(admin=email, company=company)
        
        return admin_user
    
    def get_email(self , obj):
        return obj.admin.email
    
    
    def get_phone(self , obj):
        return obj.admin.phone
    
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
    
class AdminUpdateDeleteSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField(read_only=True)
    first_name = serializers.SerializerMethodField(read_only=True)
    last_name = serializers.SerializerMethodField(read_only=True)
    company = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = AdminUser
        fields = ['id' , 'first_name' , 'last_name', 'email' , 'company']
    
    def get_email(self , obj):
        return obj.admin.email

    def get_first_name(self, obj):
        return obj.admin.first_name
    
    def get_last_name(self, obj):
        return obj.admin.last_name

    def get_company(self , obj):
        return obj.company.name
    
class CompanySerializer(serializers.ModelSerializer):
    departments = serializers.SerializerMethodField(read_only=True)
    admin = serializers.SerializerMethodField(read_only=True)
    id = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = company
        fields = '__all__'
        
    def get_id(self , obj):
        return obj.id
    
    def get_admin(self, obj):
        admins = AdminUser.objects.prefetch_related('company').filter(company=obj, is_active=True)
        serializer = AdminSerializer(admins, many=True)
        return serializer.data
    
    def get_departments(self, obj):
        admins = Departments.objects.prefetch_related('company').filter(company=obj)
        serializer = DepartmentSerializers(admins, many=True)
        return serializer.data
    
    
class CompaniesListSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    class Meta:
        model = company
        fields = ['id','name', 'logo']
        
    def get_logo(self , obj):
        if obj.logo:
            return self.context['request'].build_absolute_uri(obj.logo.url)
        return None