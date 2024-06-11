from rest_framework import serializers
from departments.models import DepartmentsDocuments , Departments
from django.utils import timezone
from teams.models import CompaniesTeam

class DepartmentsDocumentsSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField(read_only=True)
    last_name = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)
    phone = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)
    assigned_users = serializers.SerializerMethodField(read_only=True)
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
    
    def get_assigned_users(self, obj):
        return [{"id": user.id, "name": user.members.first_name} for user in obj.assigned_users.all()]
  
class DepartmentsDocumentsCreateSerializer(serializers.ModelSerializer):
    department_ids = serializers.ListField(
        child=serializers.UUIDField(format='hex_verbose'), write_only=True
    )
    user_ids = serializers.ListField(
        child=serializers.UUIDField(format='hex_verbose'), write_only=True
    )
    schedule_time = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = DepartmentsDocuments
        fields = ['id', 'name', 'file', 'department_ids', 'user_ids', 'schedule_time', 'published', 'added_by', 'created_at']

    def validate_department_ids(self, value):
        # Check if all departments are active
        for department_id in value:
            if not Departments.objects.filter(id=department_id, is_active=True).exists():
                raise serializers.ValidationError({"department not found": f"Department with ID {department_id} is not active or does not exist."})
        return value

    def validate_team_ids(self, value):
        # Check if all teams are active
        for team_id in value:
            if not CompaniesTeam.objects.filter(id=team_id, is_active=True).exists():
                raise serializers.ValidationError({"team not found": f"Team with ID {team_id} is not active or does not exist."})
        return value

    def create(self, validated_data):
        department_ids = validated_data.pop('department_ids')
        user_ids = validated_data.pop('user_ids')
        schedule_time = validated_data.pop('schedule_time', timezone.now())
        added_by = validated_data.pop('added_by')
        file = validated_data.pop('file')
        name = validated_data.pop('name')

        documents = []
        for department_id in department_ids:
            department = Departments.objects.get(id=department_id, is_active=True)
            document = DepartmentsDocuments.objects.create(
                name=name,
                added_by=added_by,
                file=file,
                department=department,
                created_at=schedule_time if schedule_time > timezone.now() else timezone.now()
            )
            document.assigned_users.set(user_ids)
            documents.append(document)
        
        return documents

    
# class DepartmentsDocumentsCreateSerializer(serializers.ModelSerializer):
#     department_ids = serializers.ListField(
#         child=serializers.UUIDField(format='hex_verbose'), write_only=True
#     )
#     schedule_time = serializers.DateTimeField(required=False, allow_null=True)

#     class Meta:
#         model = DepartmentsDocuments
#         fields = ['id', 'name', 'file', 'department_ids', 'schedule_time','published' ,'added_by' , 'created_at'] #'first_name' ,'last_name' , 'email' , 'phone' ,
        
#     def validate_department_ids(self, value):
#         # Check if all departments are active
#         for department_id in value:
#             if not Departments.objects.filter(id=department_id, is_active=True).exists():
#                 raise serializers.ValidationError({"department not found":f"Department with ID {department_id} is not active or does not exist."})
#         return value
    
#     def create(self, validated_data):
#         department_ids = validated_data.pop('department_ids')
#         schedule_time = validated_data.pop('schedule_time', timezone.now())
#         added_by = validated_data.pop('added_by')
#         file = validated_data.pop('file')
#         name = validated_data.pop('name')

#         documents = []
#         for department_id in department_ids:
#             department = Departments.objects.get(id=department_id, is_active=True)
#             document = DepartmentsDocuments.objects.create(
#                 name=name,
#                 added_by=added_by,
#                 file=file,
#                 department=department,
#                 created_at=schedule_time if schedule_time > timezone.now() else timezone.now()
#             )
#             documents.append(document)
        
#         return documents