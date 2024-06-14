from rest_framework import serializers
from accounts.models import CustomUser
from api.serializers import UserCreateSerializer


class CustomUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name' , 'last_name', 'email', 'phone', 'role', 'created_at']


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CustomUser
        fields = ['id','first_name' , 'last_name', 'email', 'phone', 'role', 'password','added_by']

    def get_password(self , obj):
        return obj.password

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value , is_available=True).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
class AdminCreationSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = '__all__'
        
    def get_role(self , obj):
        return 'Admin'