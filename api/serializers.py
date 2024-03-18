from djoser.serializers import UserCreateSerializer
from accounts.models import CustomUser, Departments, CompanyTeam
from documents.models import UserDocuments, DocumentKeyPoints, DocumentQuiz, DocumentSummary
from rest_framework import  serializers
from django.db.models import Q

class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'password')

class DepartmentSerializer(serializers.ModelSerializer):
    company = UserCreateSerializer(many=False, read_only=True)
    added_by = UserCreateSerializer(many=False, read_only=True)
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
    department = DepartmentSerializer(many=False, read_only=True)
    company = UserCreateSerializer(many=False, read_only=True)
    added_by = UserCreateSerializer(many=False, read_only=True)
    def create(self, validated_data):
        instance = CompanyTeam.objects.create_user(**validated_data)
        return instance
    class Meta:
        model = CompanyTeam
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'company', 'department', 'password', 'created_at', 'updated_at', 'added_by')

class DocumentSerializer(serializers.ModelSerializer):
    company = UserCreateSerializer(many=False, read_only=True)
    added_by = UserCreateSerializer(many=False, read_only=True)
    department = serializers.CharField()
    published = serializers.IntegerField()
    def validate_published(self, value):
        if self.context['request'].method == 'PUT' or self.context['request'].method == 'PATCH' and self.instance.id:
            if self.context['request'].data['published'] == '1':
                try:
                    dq = DocumentQuiz.objects.get(document_id=self.instance.id)
                except DocumentQuiz.DoesNotExist:
                    dq = None
                
                try:
                    ds = DocumentSummary.objects.get(document_id=self.instance.id)
                except DocumentSummary.DoesNotExist:
                    ds = None
                
                try:
                    dkp = DocumentKeyPoints.objects.get(document_id=self.instance.id)
                except DocumentKeyPoints.DoesNotExist:
                    dkp = None
                
                if ds is None or ds.content is None or ds.content == '':
                    raise serializers.ValidationError("Looks like summary is not generated. Please first generate summary")
                elif dkp is None or dkp.content is None or dkp.content == '':
                    raise serializers.ValidationError("Looks like keypoints is not generated. Please first generate keypoints")
                elif dq is None or dq.content is None or dq.content == '':
                    raise serializers.ValidationError("Looks like quiz is not generated. Please first generate quiz")
        return value
    def validate_name(self, value):
        if self.context['request'].method == 'POST':
            name_check = UserDocuments.objects.filter(name=self.context['request'].data['name'], company=self.context['request'].user )
            # print(name_check)
            if name_check is not None and len(name_check) > 0:
                raise serializers.ValidationError("That document name already exists.")
        elif self.context['request'].method == 'PUT' or self.context['request'].method == 'PATCH' and self.instance.id:
            name_check = UserDocuments.objects.filter(~Q(id=self.instance.id), name=self.context['request'].data['name'], company=self.context['request'].user)
            if name_check is not None and len(name_check) > 0:
                raise serializers.ValidationError("That document name already exists.")
        
        return value    
    class Meta:
        model = UserDocuments
        fields = ['id', 'name', 'file', 'company', 'department', 'published', 'created_date', 'updated_at', 'added_by']
    

class ReadOnlyDocumentSerializer(serializers.ModelSerializer):
    company = UserCreateSerializer(many=False, read_only=True)
    added_by = UserCreateSerializer(many=False, read_only=True)
    department = DepartmentSerializer(many=True, read_only=True)
        
    class Meta:
        model = UserDocuments
        fields = ['id', 'name', 'file', 'company', 'department', 'published', 'created_date', 'updated_at', 'added_by']
    