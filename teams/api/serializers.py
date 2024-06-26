from rest_framework import serializers
from teams.models import CompaniesTeam
from api.serializers import UserCreateSerializer
from accounts.models import CustomUser


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'phone','last_name', 'role', 'password')


from django.core.mail import send_mail
class CompaniesTeamSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField(read_only=True)
    last_name = serializers.SerializerMethodField(read_only=True)
    phone = serializers.SerializerMethodField(read_only=True)
    user_update_key = serializers.SerializerMethodField(read_only=True)
    id = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CompaniesTeam
        fields = ['id', 'members', 'company' ,'first_name' , 'last_name','phone', 'user_update_key']


    def create(self, validated_data):
        members = validated_data.pop('members')
        company = validated_data.pop('company')
        
        # # Check if an admin with the same email exists in the same company
        if CompaniesTeam.objects.filter(members=members, company=company).exists():
            raise serializers.ValidationError("User with this email already exists in this company.")

        # Check if the admin is already associated with another company
        if CompaniesTeam.objects.filter(members=members).exclude(company=company).exists():
            raise serializers.ValidationError("User is already associated with this or some another company.")

        # Create the admin user
        admin_user = CompaniesTeam.objects.create(members=members, company=company)
        
        
        return admin_user

    def get_id(self , obj):
        return obj.id
        
    def get_last_name(self , obj):
        return obj.members.last_name
    
    def get_first_name(self , obj):
        return obj.members.first_name
        
    def get_phone(self , obj):
        return str(obj.members.phone)
    
    def get_user_update_key(self , obj):
        return obj.members.id



from departments.models import Departments

class CompaniesTeamDetailFullSerializers(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    user_update_key = serializers.SerializerMethodField()
    departments_names = serializers.SerializerMethodField()

    class Meta:
        model = CompaniesTeam
        fields = "__all__"
        
    def get_email(self , obj):
        return obj.members.email
    
    def get_company(self , obj):
        return obj.company.name
    
    def get_last_name(self , obj):
        return obj.members.last_name
    
    def get_first_name(self , obj):
        return obj.members.first_name
    
    def get_phone(self , obj):
        return str(obj.members.phone)
    
    def get_user_update_key(self , obj):
        return obj.members.id
    
    def get_role(self ,obj):
        return obj.members.role

    def get_departments_names(self, obj):
        departments = Departments.objects.filter(users=obj, is_active=True)
        return [department.name for department in departments]
    
    
    
    
class CompaniesTeamDetailsSerializers(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    user_update_key = serializers.SerializerMethodField()
    departments_names = serializers.SerializerMethodField()

    class Meta:
        model = CompaniesTeam
        fields = "__all__"
        
    def get_email(self , obj):
        return obj.members.email
    
    def get_company(self , obj):
        return obj.company.name
    
    def get_last_name(self , obj):
        return obj.members.last_name
    
    def get_first_name(self , obj):
        return obj.members.first_name
    
    def get_phone(self , obj):
        return str(obj.members.phone)
    
    def get_user_update_key(self , obj):
        return obj.members.id
    
    def get_role(self ,obj):
        return obj.members.role
    
    def get_departments_names(self, obj):
        departments = Departments.objects.filter(users=obj, is_active=True)
        return [department.name for department in departments]
    
    