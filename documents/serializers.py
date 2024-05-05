from rest_framework import serializers
from departments.models import DepartmentsDocuments

class DepartmentsDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentsDocuments
        fields = '__all__'


class DepartmentsDocumentsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentsDocuments
        fields = ['name', 'file', 'department', 'published']
        
    