from rest_framework import serializers
from accounts.models import CustomUser
from api.serializers import UserCreateSerializer


class CustomUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name' , 'last_name', 'email', 'phone', 'role', 'created_at']


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.SerializerMethodField(read_only=True)
    # id = serializers.SerializerMethodField(read_only=True)
    # update_key = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CustomUser
        fields = ['id','first_name' , 'last_name', 'email', 'phone', 'role', 'password','added_by']

    # def get_id(self , obj):
    #     if obj.role == 'Admin':
    #         id = AdminUser.objects.get(admin=obj.id)
    #     elif obj.role == 'User':
    #         id = CompaniesTeam.objects.get(members=obj.id)
    #     return id.id

    def get_password(self , obj):
        return obj.password

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    

from teams.models import CompaniesTeam

class CustomUserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.SerializerMethodField(read_only=True)
    id = serializers.SerializerMethodField(read_only=True)
    user_update_key = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CustomUser
        fields = ['id','first_name' , 'last_name', 'email', 'phone', 'role', 'password','added_by' , 'user_update_key']

    def get_id(self , obj):
        id = CompaniesTeam.objects.get(members=obj.id)
        return id.id
    
    def get_user_update_key(self , obj):
        return obj.id

    def get_password(self , obj):
        return obj.password

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    


from company.models import AdminUser

class CustomAdminUpdateSerializer(serializers.ModelSerializer):
    password = serializers.SerializerMethodField(read_only=True)
    id = serializers.SerializerMethodField(read_only=True)
    admin_update_key = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CustomUser
        fields = ['id','first_name' , 'last_name', 'email', 'phone', 'role', 'password','added_by' , 'admin_update_key']

    def get_id(self , obj):
        id = AdminUser.objects.get(admin=obj.id)
        return id.id
    
    def get_admin_update_key(self , obj):
        return obj.id

    def get_password(self , obj):
        return obj.password

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    

class AdminCreationSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = '__all__'
        
    def get_role(self , obj):
        return 'Admin'