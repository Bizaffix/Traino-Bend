from djoser.serializers import UserCreateSerializer
from accounts.models import CustomUser, CompanyTeam
from departments.models import Departments , DepartmentsDocuments
from documents.serializers import DepartmentsDocumentsSerializer
from documents.models import UserDocuments, DocumentKeyPoints, DocumentQuiz, DocumentSummary
from rest_framework import  serializers
from django.db.models import Q

class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'password')

class DepartmentSerializers(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField(read_only=True)
    user_update_key = serializers.SerializerMethodField(read_only=True)
    user_first_name = serializers.SerializerMethodField(read_only=True)
    user_last_name = serializers.SerializerMethodField(read_only=True)
    user_phone = serializers.SerializerMethodField(read_only=True)
    # documents = serializers.SerializerMethodField(read_only=True)
    user_added_by = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Departments
        fields ='__all__'

    def get_user_email(self , obj):
        return [user.members.email for user in obj.users.all()]
    
    def get_user_update_key(self , obj):
        return [user.members.id for user in obj.users.all()]

    def get_user_first_name(self , obj):
        return [user.members.first_name for user in obj.users.all()]
    
    def get_user_last_name(self , obj):
        return [user.members.last_name for user in obj.users.all()]
    
    def get_user_phone(self , obj):
        return [str(user.members.phone) for user in obj.users.all()]
    
    def get_user_added_by(self , obj):
        return [str(user.members.added_by) for user in obj.users.all()]
        
class DepartmentRUDSerializers(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(read_only=True)
    company = serializers.SerializerMethodField()
    added_by = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()
    class Meta:
        model = Departments
        fields ='__all__'

    def get_id(self , obj):
        return obj.id

    def get_company(self , obj):
        return obj.company.name
    
    def get_added_by(self, obj):
        return obj.added_by.email
    
    def get_users(self, obj):
        return [user.members.email for user in obj.users.all()]

class CompanyDepartmentsListSerializers(serializers.ModelSerializer):
    class Meta:
        model = Departments
        fields = '__all__'    

class CompanyDepartmentsSerializers(serializers.ModelSerializer):
    company_id = serializers.UUIDField()
    class Meta:
        model = Departments
        fields = '__all__'    

    def to_representation(self, instance):
        company_id = instance['company_id']
        try:
            company_departments = Departments.objects.filter(company_id=company_id)
            serializer = CompanyDepartmentsListSerializers(company_departments, many=True)
            return serializer.data
        except Departments.DoesNotExist:
            raise serializers.ValidationError("Company with given ID does not exist.")


class DepartmentListSerializers(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(read_only=True)
    company = serializers.SerializerMethodField()
    added_by = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField(read_only=True)
    documents = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Departments
        fields ='__all__'

    def get_id(self , obj):
        return obj.id
    
    

    def get_company(self , obj):
        return obj.company.name
    
    def get_added_by(self, obj):
        return obj.added_by.email
    
    def get_users(self, obj):
        # Retrieve emails of users associated with the department
        # users_emails = [user.email for user in obj.customuser_set.all()]  
        return [user.members.email for user in obj.users.all()]

    def get_documents(self, obj):
        admins = DepartmentsDocuments.objects.prefetch_related('department').filter(department=obj, is_active=True)
        serializer = DepartmentsDocumentsSerializer(admins, many=True)
        return serializer.data    
    
    def get_created_at(self ,obj):
        return obj.created_at
class CompanyTeamSerializer(serializers.ModelSerializer):
    department = DepartmentSerializers(many=False, read_only=True)
    company = UserCreateSerializer(many=False, read_only=True)
    added_by = UserCreateSerializer(many=False, read_only=True)

    class Meta:
        model = CompanyTeam
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'company', 'department', 'password', 'created_at', 'updated_at', 'added_by')
    
    def create(self, validated_data):
        instance = CompanyTeam.objects.create_user(**validated_data)
        return instance
        
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
        elif self.context['request'].method == 'POST':
            value = False
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
    department = DepartmentSerializers(many=True, read_only=True)
        
    class Meta:
        model = UserDocuments
        fields = ['id', 'name', 'file', 'company', 'department', 'published', 'created_date', 'updated_at', 'added_by']

class DocumentSummarySerializer(serializers.ModelSerializer):
    added_by = UserCreateSerializer(many=False, read_only=True)

    def validate_prompt_text(self, value):
        # Check if the request method is PUT, PATCH, or POST
        if self.context['request'].method in ['PUT', 'PATCH', 'POST']:
            # Check if prompt_text is empty
            if not value.strip():
                # If prompt_text is empty, set default value
                value = 'concise summary'
        return value    
    
    document = serializers.UUIDField(write_only=True)
    class Meta:
        model = DocumentSummary
        fields = ['id', 'content', 'company','prompt_text', 'document', 'created_date', 'updated_at', 'added_by']

    def create(self, validated_data):
        document_id = validated_data.pop('document', None)
        if document_id is None:
            raise serializers.ValidationError("document_id is required.")

        document_summary = DocumentSummary.objects.create(document_id=document_id, **validated_data)
        return document_summary

    def get_document(self, obj):
        return obj.document.id


class DocumentKeyPointsSerializer(serializers.ModelSerializer):
    added_by = UserCreateSerializer(many=False, read_only=True)

    def validate_prompt_text(self, value):
        # Check if the request method is PUT, PATCH, or POST
        if self.context['request'].method in ['PUT', 'PATCH', 'POST']:
            # Check if prompt_text is empty
            if not value.strip():
                # If prompt_text is empty, set default value
                value = 'key points'
        return value

    document = serializers.UUIDField(write_only=True)

    class Meta:
        model = DocumentKeyPoints
        fields = ['id', 'content', 'company', 'prompt_text', 'document', 'created_date', 'updated_at', 'added_by']

    def create(self, validated_data):
        document_id = validated_data.pop('document', None)
        if document_id is None:
            raise serializers.ValidationError("document_id is required.")

        document_key_points = DocumentKeyPoints.objects.create(document_id=document_id, **validated_data)
        return document_key_points

    def get_document(self, obj):
        return obj.document.id
class ReadOnlyDocumentSummarySerializer(serializers.ModelSerializer):
    document = ReadOnlyDocumentSerializer(many=False, read_only=True)
    added_by = UserCreateSerializer(many=False, read_only=True)
       
    class Meta:
        model = DocumentSummary
        fields = ['id', 'content', 'prompt_text', 'document', 'created_date', 'updated_at', 'added_by']    

class DocumentKeypointsSerializer(serializers.ModelSerializer):
    document = serializers.CharField()
    added_by = UserCreateSerializer(many=False, read_only=True)
    def validate_prompt_text(self, value):
        if self.context['request'].method == 'PUT' or self.context['request'].method == 'PATCH' or self.context['request'].method == 'POST':
            if self.context['request'].data['prompt_text'] == '':
                value = 'concise outline in numeric order list'
        return value    
       
    class Meta:
        model = DocumentKeyPoints
        fields = ['id', 'content', 'prompt_text', 'document', 'created_date', 'updated_at', 'added_by']

class ReadOnlyDocumentKeypointsSerializer(serializers.ModelSerializer):
    document = ReadOnlyDocumentSerializer(many=False, read_only=True)
    added_by = UserCreateSerializer(many=False, read_only=True)
       
    class Meta:
        model = DocumentKeyPoints
        fields = ['id', 'content', 'prompt_text', 'document', 'created_date', 'updated_at', 'added_by']    


from teams.models import CompaniesTeam


class AddUserToDepartmentSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=CompaniesTeam.objects.filter(is_active=True))
    department_id = serializers.PrimaryKeyRelatedField(queryset=Departments.objects.filter(is_active=True))
    
    def validate(self, data):
        user = data['user_id']
        department = data['department_id']
        if user in department.users.filter(is_active=True):
            raise serializers.ValidationError("User is already in this department.")
        return data

    def update(self, instance, validated_data):
        user = validated_data['user_id']
        instance.users.add(user)
        return instance