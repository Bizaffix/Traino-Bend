from rest_framework import serializers
from departments.models import DepartmentsDocuments , Departments
from django.utils import timezone

class DepartmentsDocumentsSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField(read_only=True)
    last_name = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)
    phone = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = DepartmentsDocuments
        fields = '__all__'

    def get_first_name(self , obj):
        return obj.added_by.first_name
    
    def get_last_name(self , obj):
        return obj.added_by.last_name
    
    def get_email(self , obj):
        return obj.added_by.email
    
    def get_phone(self , obj):
        return str(obj.added_by.phone)
        
    def get_created_at(self, obj):
        return obj.created_at
    
class DepartmentsDocumentsCreateSerializer(serializers.ModelSerializer):
    department_ids = serializers.ListField(
        child=serializers.UUIDField(format='hex_verbose'), write_only=True
    )
    schedule_time = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = DepartmentsDocuments
        fields = ['id', 'name', 'file', 'department_ids', 'schedule_time','published' ,'added_by' , 'created_at'] #'first_name' ,'last_name' , 'email' , 'phone' ,
        
    def validate_department_ids(self, value):
        # Check if all departments are active
        for department_id in value:
            if not Departments.objects.filter(id=department_id, is_active=True).exists():
                raise serializers.ValidationError({"department not found":f"Department with ID {department_id} is not active or does not exist."})
        return value
    
    def create(self, validated_data):
        department_ids = validated_data.pop('department_ids')
        schedule_time = validated_data.pop('schedule_time', timezone.now())
        added_by = validated_data.pop('added_by')
        name = validated_data.pop('name')

        documents = []
        for department_id in department_ids:
            department = Departments.objects.get(id=department_id, is_active=True)
            document = DepartmentsDocuments.objects.create(
                name=name,
                added_by=added_by,
                department=department,
                created_at=schedule_time if schedule_time > timezone.now() else timezone.now()
            )
            documents.append(document)
        
        return documents