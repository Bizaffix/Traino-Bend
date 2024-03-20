from rest_framework.response import Response
from accounts.models import Departments, CompanyTeam, CustomUser 
from documents.models import UserDocuments, DocumentSummary, DocumentKeyPoints, DocumentQuiz, DocumentTeam
from api.serializers import DepartmentSerializer, CompanyTeamSerializer, UserCreateSerializer, DocumentSerializer, ReadOnlyDocumentSerializer, DocumentSummarySerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter

def assignDocumentToUser(user, doc, department):
    try:
        das = DocumentTeam.objects.get(user_id = user.id, document_id = doc.id, department_id = department.id)
    except DocumentTeam.DoesNotExist:
        das = None


    if das is None:
        das = DocumentTeam(user_id = user.id, document_id = doc.id, department_id = department.id, is_assigned = False, notify_frequency = 0)
        das.save()
    
class DepartmentModelViewSet(viewsets.ModelViewSet):
    queryset = Departments.objects.all()
    serializer_class = DepartmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']


    def get_queryset(self):
        return Departments.objects.filter(company_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['company'] = self.request.user
        serializer.validated_data['added_by'] = self.request.user
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class CompanyTeamModelViewSet(viewsets.ModelViewSet):
    queryset = CompanyTeam.objects.all()
    serializer_class = CompanyTeamSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']

    def get_queryset(self):
        return CompanyTeam.objects.filter(company_id=self.request.user.id)
    
    def create(self, request, *args, **kwargs):
        # request.data['company'] = self.request.user.pk
        # request.data['added_by'] = self.request.user.pk
        # request.data['role'] = 'User'
        # request.data['is_staff'] = 1

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['company'] = self.request.user
        serializer.validated_data['added_by'] = self.request.user
        serializer.validated_data['role'] = 'User'
        serializer.validated_data['is_staff'] = 1
        serializer.validated_data['department'] = Departments.objects.get(pk=request.data['department'])
        self.perform_create(serializer)

        company_documents = UserDocuments.objects.filter(company_id = self.request.user.id, department = int(request.data['department']))
        for company_document in company_documents:
            assignDocumentToUser(CustomUser.objects.get(pk= int(serializer.data['id'])), company_document, Departments.objects.get(pk=request.data['department']))
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class DocumentModelViewSet(viewsets.ModelViewSet):
    queryset = UserDocuments.objects.all()
    serializer_class = DocumentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']


    def get_queryset(self):
        return UserDocuments.objects.filter(company_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        # request.data['company'] = self.request.user.pk
        # request.data['added_by'] = self.request.user.pk
        if 'published' in request.data:
            request.data.pop('published')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['company'] = self.request.user
        serializer.validated_data['added_by'] = self.request.user
        
        validated_data = serializer.validated_data
        new_document = UserDocuments.objects.create(name = validated_data['name'], file = validated_data['file'], company_id = self.request.user.pk, added_by_id = self.request.user.pk)
        new_document.save()
        
        department_ids = request.data['department'].split(',')
        for department_id in department_ids:
            department_object = Departments.objects.get(pk= int(department_id))
            new_document.department.add(department_object)
            user_teams = CompanyTeam.objects.filter(company_id = self.request.user.id, department_id = department_object.id ).order_by('first_name')
            for user_team in user_teams:
                assignDocumentToUser(user_team, new_document, department_object)
        
        serializer = ReadOnlyDocumentSerializer(new_document)
        headers = self.get_success_headers(serializer.data)

        try:
            dq = DocumentQuiz.objects.get(document_id=new_document.id)
        except DocumentQuiz.DoesNotExist:
            dq = None
        
        try:
            ds = DocumentSummary.objects.get(document_id=new_document.id)
        except DocumentSummary.DoesNotExist:
            ds = None
        
        try:
            dkp = DocumentKeyPoints.objects.get(document_id=new_document.id)
        except DocumentKeyPoints.DoesNotExist:
            dkp = None

        if dq is None:
            dq = DocumentQuiz(name=str(new_document.name), prompt_text='25 multiple choice questions', company = self.request.user, content='', document_id= str(new_document.id))
            dq.save()
        if ds is None:
            ds = DocumentSummary(content='', prompt_text='concise summary', company = self.request.user, document_id= str(new_document.id))
            ds.save()
        if dkp is None:
            dkp = DocumentKeyPoints(content='', prompt_text='concise outline in numeric order list', company = self.request.user, document_id= str(new_document.id))
            dkp.save()


        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)  

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        department_ids = ''
        if 'department' in request.data:
            department_ids = request.data['department']
            request.data.pop('department')
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        
        if department_ids is not None:
            for doc_dept in instance.department.all():
               instance.department.remove(doc_dept) 
            department_ids = department_ids.split(',')
            for department_id in department_ids:
                department_object = Departments.objects.get(pk= int(department_id))
                instance.department.add(department_object)
                user_teams = CompanyTeam.objects.filter(company_id = self.request.user.id, department_id = department_object.id ).order_by('first_name')
                for user_team in user_teams:
                    assignDocumentToUser(user_team, instance, department_object)
        
        serializer = ReadOnlyDocumentSerializer(instance)

        try:
            dq = DocumentQuiz.objects.get(document_id=instance.id)
        except DocumentQuiz.DoesNotExist:
            dq = None
        
        try:
            ds = DocumentSummary.objects.get(document_id=instance.id)
        except DocumentSummary.DoesNotExist:
            ds = None
        
        try:
            dkp = DocumentKeyPoints.objects.get(document_id=instance.id)
        except DocumentKeyPoints.DoesNotExist:
            dkp = None

        if dq is None:
            dq = DocumentQuiz(name=str(instance.name), prompt_text='25 multiple choice questions', content='', document_id= str(instance.id))
            dq.save()
        if ds is None:
            ds = DocumentSummary(content='', prompt_text='concise summary', document_id= str(instance.id))
            ds.save()
        if dkp is None:
            dkp = DocumentKeyPoints(content='', prompt_text='concise outline in numeric order list', document_id= str(instance.id))
            dkp.save()

        return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ReadOnlyDocumentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ReadOnlyDocumentSerializer(queryset, many=True)
        return Response(serializer.data) 

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ReadOnlyDocumentSerializer(instance)
        return Response(serializer.data) 

class DocumentSummaryModelViewSet(viewsets.ModelViewSet):
    queryset = DocumentSummary.objects.all()
    serializer_class = DocumentSummarySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['content', 'prompt_text']


    def get_queryset(self):
        return DocumentSummary.objects.filter(company_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['company'] = self.request.user
        serializer.validated_data['added_by'] = self.request.user
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

