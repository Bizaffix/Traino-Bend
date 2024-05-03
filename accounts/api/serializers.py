from rest_framework import serializers
from accounts.models import CustomUser
from api.serializers import UserCreateSerializer


class CustomUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'role', 'created_at']


class AdminCreationSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = '__all__'
        
    def get_role(self , obj):
        return 'Admin'