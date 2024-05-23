from rest_framework import serializers
from teams.models import CompaniesTeam
from api.serializers import UserCreateSerializer
from accounts.models import CustomUser


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'phone','last_name', 'role', 'password')

class CompaniesTeamSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField(read_only=True)
    last_name = serializers.SerializerMethodField(read_only=True)
    phone = serializers.SerializerMethodField(read_only=True)
    user_update_key = serializers.SerializerMethodField(read_only=True)
    id = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CompaniesTeam
        fields = ['id', 'members', 'company' ,'first_name' , 'last_name','phone', 'user_update_key']

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
    
    
class CompaniesTeamDetailsSerializers(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    user_update_key = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
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
    
    def get_department(self, obj):
        # Assuming a reverse relation from CompaniesTeam to Departments
        department = obj.departments_set.first()  # Assuming each user belongs to only one department
        if department:
            return department.name
        else:
            return None