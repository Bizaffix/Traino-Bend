from djoser.serializers import UserCreateSerializer
from accounts.models import CustomUser, Departments, CompanyTeam
from rest_framework import  serializers
from django.db.models import Q

class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'password')

class DepartmentSerializer(serializers.ModelSerializer):
    company = UserCreateSerializer()
    added_by = UserCreateSerializer()
    def validate_name(self, value):
        if self.context['request'].method == 'POST':
            name_check = Departments.objects.filter(name=self.context['request'].data['name'], company=self.context['request'].user )
            # print(name_check)
            if name_check is not None and len(name_check) > 0:
                raise serializers.ValidationError("That department name already exists.")
        elif self.context['request'].method == 'PUT' or self.context['request'].method == 'PATCH' and self.instance.id:
            name_check = Departments.objects.filter(~Q(id=self.instance.id), name=self.context['request'].data['name'], company=self.context['request'].user)
            if name_check is not None and len(name_check) > 0:
                raise serializers.ValidationError("That department name already exists.")
        
        return value    
    class Meta:
        model = Departments
        fields = ['id', 'name', 'company', 'created_at', 'updated_at', 'added_by']

class CompanyTeamSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer()
    company = UserCreateSerializer()
    added_by = UserCreateSerializer()
    def create(self, validated_data):
        instance = CompanyTeam.objects.create_user(**validated_data)
        return instance
    class Meta:
        model = CompanyTeam
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'company', 'department', 'password', 'created_at', 'updated_at', 'added_by')
