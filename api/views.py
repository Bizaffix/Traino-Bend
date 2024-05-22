from rest_framework.response import Response
from accounts.models import CompanyTeam, CustomUser 
from departments.models import Departments
from rest_framework.generics import CreateAPIView, RetrieveAPIView , UpdateAPIView, DestroyAPIView, ListAPIView
from documents.models import UserDocuments, DocumentSummary, DocumentKeyPoints, DocumentQuiz, DocumentTeam
from api.serializers import DepartmentSerializers, DepartmentListSerializers ,DepartmentRUDSerializers,CompanyTeamSerializer, UserCreateSerializer, DocumentSerializer, ReadOnlyDocumentSerializer, DocumentSummarySerializer, ReadOnlyDocumentSummarySerializer, DocumentKeypointsSerializer, ReadOnlyDocumentKeypointsSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import  serializers
from django.contrib.auth.models import User
from .permissions import IsAdminUserOrReadOnly
import os
from rest_framework.views import APIView
from langchain_community.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain_community.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import PyPDFLoader
from PyPDF2 import PdfReader
from company.models import AdminUser
from teams.models import CompaniesTeam
from langchain.prompts import PromptTemplate
openai_api_key = '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'
os.environ['OPENAI_API_KEY'] = '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'
from departments.models import DepartmentsDocuments


def readPDFFile(pdf_file_path):
    pdf_reader = PdfReader(pdf_file_path)
    text = ""
    #pageno = 0
    for page in pdf_reader.pages:
        # pageNoinfo = "\t this page Number is :" + str(pageno)
        #text += (page.extract_text() + pageNoinfo)
        text += (page.extract_text())
        #pageno = pageno + 1
    return text


def assignDocumentToUser(user, doc, department):
    try:
        das = DocumentTeam.objects.get(user_id = user.id, document_id = doc.id, department_id = department.id)
    except DocumentTeam.DoesNotExist:
        das = None


    if das is None:
        das = DocumentTeam(user_id = user.id, document_id = doc.id, department_id = department.id, is_assigned = False, notify_frequency = 0)
        das.save()

def generateDocumentSummary(request):
    summary_id = request.data.get("summary_id")
    document_id = request.data.get("document_id")
    prompt_text = request.data.get("prompt_text")
    document_summary = 'Oops! Summary not generated please try with some other document.'
    document = DepartmentsDocuments.objects.get(id=document_id)
    if document.file.path is not None:
        try:
            # print("test: 1")
            # Instantiate the LLM model
            #llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
            llm = ChatOpenAI(model_name='gpt-3.5-turbo')
            # print("test: 2")
            # print(document.file.path)

            loader = PyPDFLoader(document.file.path)
            #docs = loader.load_and_split()
            
            pages = loader.load()
            text = ""
            for page in pages:
                text+=page.page_content
            text= text.replace('\t', ' ')
            text= text.replace('\xa0', '')

            # print(len(text))

            #splits a long document into smaller chunks that can fit into the LLM's 
            #model's context window
            
            text_splitter = CharacterTextSplitter(
                    separator="\n",
                    chunk_size=1000,
                    chunk_overlap=100
                )
            # print(text_splitter)
            
            #create_documents() create documents froma list of texts
            
            text = text_splitter.create_documents([text])
            # print(len(docs))
            # print(docs)

            # print("test: 4")

            # Define prompt
            prompt_template = """You are required to generate """+prompt_text+""" based on the provided text:
            {text}
            CONCISE SUMMARY:"""

            

            prompt_template = PromptTemplate(template=prompt_template, input_variables=["text"])

            # Text summarization
            chain = load_summarize_chain(llm, chain_type='stuff', prompt=prompt_template)
            # print("test: 5")
            document_summary = chain.run(text)
            # print("test: 6")
            # print(document_summary)

            doc_summary = DocumentSummary.objects.get(id = summary_id)
            doc_summary.content = document_summary
            doc_summary.prompt_text = prompt_text
            doc_summary.save()
        except Exception as error:
            if error.code == 'insufficient_quota':
                raise serializers.ValidationError("You exceeded your current quota, please check your plan and billing details.")
            else:
                print(error)
                raise serializers.ValidationError("Your document content is too large, Please try with some other document.")
            
    else:
        raise serializers.ValidationError("Invalide document file selected.")


def generateDocumentKeypoints(keypoint_id, document_id, prompt_text):
    document_keypoints = 'Oops! Keypoints not generated please try with some other document.'
    document = UserDocuments.objects.get(id=document_id)
    if document.file.path is not None:
        try:
            #print("test: 1")
            # Instantiate the LLM model
            #llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
            llm = ChatOpenAI(model_name='gpt-3.5-turbo')
            #print("test: 2")
            print(document.file.path)
            text = readPDFFile(document.file.path)
            #print("test: 3")

            loader = PyPDFLoader(document.file.path)
            # text = loader.load_and_split()
            # print(text)

            pages = loader.load()
            text = ""
            for page in pages:
                text+=page.page_content
            text= text.replace('\t', ' ')
            text= text.replace('\xa0', '')

            #print(len(text))

            #splits a long document into smaller chunks that can fit into the LLM's 
            #model's context window
            
            text_splitter = CharacterTextSplitter(
                    separator="\n",
                    chunk_size=4000,
                    chunk_overlap=200
                )
            # print(text_splitter)
            
            #create_documents() create documents froma list of texts
            
            text = text_splitter.create_documents([text])

            text_chunk_index = 0
            for text_chunk in text:
                # print(text_chunk.page_content)
                # print('-----------------------')
                text[text_chunk_index].page_content = text_chunk.page_content.replace('\n', '')
                text_chunk_index += 1


            #print(text)
            #print("test: 4")

            # Define prompt
            prompt_template = """You are required to generate """+prompt_text+""" based on the provided text:
            {text}
            CONCISE OUTLINE:"""

            # prompt_template = """You are required to generate 25 multiple choice questions having four options and correct answer in json format based on the provided text:
            # {text}
            # MCQ QUIZ:"""

            prompt_template = PromptTemplate(template=prompt_template, input_variables=["text"])

            

            # Text summarization
            chain = load_summarize_chain(llm, chain_type='stuff', prompt=prompt_template)
            #print("test: 5")
            document_keypoints = chain.run(text)
            #print(len(data['document_keypoints']))
            #print(data['document_keypoints'])
            #print("test: 6")
            doc_keypoints = DocumentKeyPoints.objects.get(pk = keypoint_id)
            doc_keypoints.content = document_keypoints
            doc_keypoints.prompt_text = prompt_text
            doc_keypoints.save()
        except Exception as error:
            if error.code == 'insufficient_quota':
                raise serializers.ValidationError("You exceeded your current quota, please check your plan and billing details.")
            else:
                raise serializers.ValidationError("Your document content is too large, Please try with some other document.")
            print(error)
    else:
        raise serializers.ValidationError("Invalide document file selected.")

from rest_framework import serializers


class DepartmentCreateApiview(CreateAPIView):
    serializer_class = DepartmentSerializers
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserOrReadOnly]
    
    def perform_create(self, serializer):
        # Extract company ID from the request data
        company_id_from_request = self.request.data.get('company')
        name = self.request.data.get('name')
        try:
            company_name = Departments.objects.get(name=name)
            if company_name:
                raise serializers.ValidationError(
                    {"Department Exists": f"Department with this name {name} already exists"})
        except Departments.DoesNotExist:
            # User does not exist, so continue with user creation
            pass
        # Get the admin user associated with the request user
        try:
            admin_user = AdminUser.objects.get(admin=self.request.user, is_active=True)
        except AdminUser.DoesNotExist:
            raise serializers.ValidationError({"Error": "Your account is deleted as Admin by Super Admin. You can no Longer access this feature"})

        # Check if the company ID from the request matches the company associated with the admin user
        if str(admin_user.company.id) != company_id_from_request:
            raise serializers.ValidationError({"Access Denied": "You are not allowed to create departments in this company."})

        # Save the department with the associated admin user
        serializer.save(added_by=self.request.user)
    
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt    

class DepartmentRetrieveApiView(RetrieveAPIView , UpdateAPIView , DestroyAPIView):
    serializer_class = DepartmentRUDSerializers
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserOrReadOnly, IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    queryset = Departments.objects.filter(is_active=True)
    lookup_field = 'id'

    # def get(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     print(self.request.user.role)
    #     admin = AdminUser.objects.get(admin=self.request.user)
    #     if str(instance.company.id) == str(admin.company.id):
    #         if admin.is_active==True:
    #             return super().retrieve(request, *args, **kwargs)
    #         return Response({"Account Error":"Your Profile is restricted . You are not allowed to perform this action"}, status=status.HTTP_403_FORBIDDEN)
    #     return Response({"Account Error":"Your Profile is Not Authorized for this request as you are requesting data for unknown company department."},status=status.HTTP_401_UNAUTHORIZED)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def put(self , request , *args, **kwargs):
        instance = self.get_object()
        admin = AdminUser.objects.get(admin=self.request.user)
        if str(instance.company.id) == str(admin.company.id):
            if admin.is_active==True:
                Departments.objects.get(id=self.kwargs['id'])
                return self.update(request, *args , **kwargs)
            return Response({"Account Error":"Your Profile is restricted . You are not allowed to perform this action"},status=status.HTTP_404_NOT_FOUND)
        return Response({"Account Error":"Your Profile is Not Authorized for this request as you are requesting data for unknown company department."},status=status.HTTP_401_UNAUTHORIZED)
    
    @method_decorator(csrf_exempt)
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        admin = AdminUser.objects.get(admin=self.request.user)
        if str(instance.company.id) == str(admin.company.id):
            if admin.is_active==True:
                instance.is_active = False
                instance.save()
                return Response({"Delete Status": "Successfully deleted the department." , "Department_id":instance.id},status=status.HTTP_202_ACCEPTED)
            return Response({"Account Error":"Account did not found"},status=status.HTTP_404_NOT_FOUND)
        return Response({"Account Error":"Your Profile is Not Authorized for this request as you are requesting data for unknown company department."},status=status.HTTP_401_UNAUTHORIZED)

class DepartmentListApiView(ListAPIView):
    serializer_class = DepartmentListSerializers
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'id', 'company__name']
    ordering_fields = ['name' , 'id', 'company' , 'users' , 'created_at', 'updated_at']
    ordering = ['name','id', 'company' , 'users' , 'created_at', 'updated_at']  # Default ordering (A-Z by company_name)
    queryset = Departments.objects.filter(is_active=True)

    def get_queryset(self):
        """
        Optionally restricts the returned administrators to a given company,
        by filtering against a `company_id` query parameter in the URL.
        """
        if (self.request.user.role == "Admin"):
            company_id = self.request.query_params.get('company_id', None)
            # print(company_id)
            admin = AdminUser.objects.get(admin=self.request.user)
            queryset = Departments.objects.filter(is_active=True)
            # print(admin.is_active)
            # print(str(company_id) == str(admin.company.id))
            if str(company_id) == str(admin.company.id):
                if admin.is_active==True:
                    if queryset is not None and company_id is not None:
                        queryset = queryset.filter(company__id=company_id)
                    return queryset
                else:
                        raise serializers.ValidationError({"Permission Denied":"Your Account is Restricted. You cannot Perform this task"})
            else:
                raise serializers.ValidationError({"Permission Denied":"You are not allowed to view departments of this company"})
        # elif (self.request.user.role == "User"):
        #     user = self.request.user
        #     company_id = self.request.query_params.get('company_id', None)
        #     print(company_id)
        #     user_teams = CompaniesTeam.objects.get(members=user.id, is_active=True)
        #     user_departments = Departments.objects.filter(users__in=user_teams, is_active=True)
        #     queryset = Departments.objects.filter(id__in=user_departments)
        #     if company_id:
        #         queryset = queryset.filter(company__id=company_id)
        #         return queryset
        #     else:
        #         raise serializers.ValidationError({"Permission Denied": "You are not allowed to view departments"}, status=status.HTTP_403_FORBIDDEN)
        else:
            queryset = Departments.objects.filter(is_active=True)
            company_id = self.request.query_params.get('company_id', None)
            if company_id is not None:
                queryset = queryset.filter(company__id=company_id)
            return queryset
            
from .serializers import CompanyDepartmentsSerializers

class CompanyDepartmentsListAPIView(ListAPIView):
    serializer_class = CompanyDepartmentsSerializers
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    queryset = Departments.objects.filter(is_active=True)
    
    def get_queryset(self):
        """
        This view returns a list of active departments for a given company,
        filtered by the 'company_id' query parameter. Additionally, it ensures
        that only the admins of the specified company can view the departments.
        """
        company_id = self.request.query_params.get('company_id')
        if company_id is not None:
            # Ensure the user is the admin of the company
            if not self.request.user.is_admin_of(company_id):
                return Departments.objects.none()  # Returns an empty queryset

            return Departments.objects.filter(company=company_id, is_active=True)
        return Departments.objects.filter(is_active=True)

    def get_permissions(self):
        """
        Get the list of permissions that this view requires.
        """
        if self.request.method in ['GET']:
            return [IsAdminUserOrReadOnly()]
        return [permission() for permission in self.permission_classes]
        
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
    search_fields = ['name', 'id', 'company__name']
    ordering_fields = ['name' , 'id', 'company' , 'users' , 'created_at', 'updated_at']
    ordering = ['name','id', 'company' , 'users' , 'created_at', 'updated_at']  # Default ordering (A-Z by company_name)


    def get_queryset(self):
        return UserDocuments.objects.filter(company_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        # request.data['company'] = self.request.user.pk
        # request.data['added_by'] = self.request.user.pk
        if 'published' in request.data:
            request.data.pop('published')
        request.data['published'] = 0
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
            dq = DocumentQuiz(name=str(new_document.name), prompt_text='25 multiple choice questions', company = self.request.user, content='', document_id= str(new_document.id), added_by_id= str(self.request.user.id))
            dq.save()
        if ds is None:
            ds = DocumentSummary(content='', prompt_text='concise summary', company = self.request.user, document_id= str(new_document.id), added_by_id= str(self.request.user.id))
            ds.save()
        if dkp is None:
            dkp = DocumentKeyPoints(content='', prompt_text='concise outline in numeric order list', company = self.request.user, document_id= str(new_document.id), added_by_id= str(self.request.user.id))
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
            dq = DocumentQuiz(name=str(new_document.name), prompt_text='25 multiple choice questions', company = self.request.user, content='', document_id= str(new_document.id), added_by_id= str(self.request.user.id))
            dq.save()
        if ds is None:
            ds = DocumentSummary(content='', prompt_text='concise summary', company = self.request.user, document_id= str(new_document.id), added_by_id= str(self.request.user.id))
            ds.save()
        if dkp is None:
            dkp = DocumentKeyPoints(content='', prompt_text='concise outline in numeric order list', company = self.request.user, document_id= str(new_document.id), added_by_id= str(self.request.user.id))
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


# from openai import OpenAI
import openai

class DocumentSummaryModelViewSet(viewsets.ModelViewSet):
    queryset = DocumentSummary.objects.all()
    serializer_class = DocumentSummarySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserOrReadOnly]
    search_fields = ['id' ,'content', 'prompt_text','name', 'id', 'company__name', 'document__name']
    ordering_fields = ['name' , 'id', 'company' , 'document' , 'created_at', 'updated_at']
    ordering = ['name','id', 'company' , 'users' , 'created_at', 'updated_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == "Super Admin":
            return DocumentSummary.objects.all()
        elif user.role == "Admin":
            try:
                admin = AdminUser.objects.get(admin=user)
                company = admin.company_id
                return DocumentSummary.objects.filter(company=company)
            except AdminUser.DoesNotExist:
                raise serializers.ValidationError({"Access Denied": "Your Account is Restricted"})
        elif user.role == "User":
            try:
                user_teams = CompaniesTeam.objects.filter(members=user, is_active=True)
                if user_teams.exists():
                    company_ids = user_teams.values_list('company_id', flat=True)
                    return DocumentSummary.objects.filter(company__in=company_ids)
                else:
                    raise serializers.ValidationError({"Access Denied": "Your Account is Restricted"})
            except CompaniesTeam.DoesNotExist:
                raise serializers.ValidationError({"Access Denied": "Your Account is Restricted"})
        else:
            return Response({"Access Denied": "You are not authorized for this request"})

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == "Admin":
            try:
                admin_user = AdminUser.objects.get(admin=user, is_active=True)
                company = admin_user.company_id
                requested_company_id = serializer.validated_data.get('company')
                print(company)
                print(requested_company_id.id)
                if requested_company_id.id != company:
                    raise serializers.ValidationError("You can only create summaries for your own company.")
                
                # Use OpenAI to create summary
                document_content = serializer.validated_data.get('content')
                summary = self.generate_summary(document_content)
                serializer.save(added_by=user, summary=summary)
                
            except AdminUser.DoesNotExist:
                raise serializers.ValidationError("Admin user not found.")
        else:
            raise serializers.ValidationError("Only Admins can create document summaries.")
    
    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        if (user.role == "Admin" and instance.added_by == user):
            document_content = serializer.validated_data.get('content', instance.content)
            summary = self.generate_summary(document_content)
            serializer.save(summary=summary)
            return serializer.data
        else:
            raise serializers.ValidationError("You do not have permission to update this summary.")

    def perform_destroy(self, instance):
        user = self.request.user
        if (user.role == "Admin" and instance.added_by == user):
            # instance.is_active = False
            # instance.save()
            obj_id = instance.id
            instance.delete()
            return Response({"Response":"Successfully Deleted the Summary.","id": obj_id})
        else:
            raise serializers.ValidationError("You do not have permission to delete this summary.")
    
    def generate_summary(self, content):
        openai.api_key = openai_api_key
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",
            prompt=f"Summarize the following document:\n\n{content}",
            max_tokens=150
        )
        summary = response.choices[0].text.strip()
        return summary

from .serializers import DocumentKeyPointsSerializer
class DocumentKeyPointsModelViewSet(viewsets.ModelViewSet):
    queryset = DocumentKeyPoints.objects.filter(is_active=True)
    serializer_class = DocumentKeyPointsSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserOrReadOnly]
    search_fields = ['id' ,'content', 'prompt_text','name', 'id', 'company__name', 'document__name']
    ordering_fields = ['name' , 'id', 'company' , 'document' , 'created_at', 'updated_at']
    ordering = ['name','id', 'company' , 'users' , 'created_at', 'updated_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == "Super Admin":
            return DocumentKeyPoints.objects.filter(is_active=True)
        elif user.role == "Admin":
            try:
                admin = AdminUser.objects.get(admin=user, is_active=True)
                company = admin.company_id
                return DocumentKeyPoints.objects.filter(company=company)
            except AdminUser.DoesNotExist:
                raise serializers.ValidationError({"Access Denied": "Your Account is Restricted"})
        elif user.role == "User":
            try:
                user_teams = CompaniesTeam.objects.filter(members=user, is_active=True)
                if user_teams.exists():
                    company_ids = user_teams.values_list('company_id', flat=True)
                    return DocumentKeyPoints.objects.filter(company__in=company_ids)
                else:
                    raise serializers.ValidationError({"Access Denied": "Your Account is Restricted"})
            except CompaniesTeam.DoesNotExist:
                raise serializers.ValidationError({"Access Denied": "Your Account is Restricted"})
        else:
            return Response({"Access Denied": "You are not authorized for this request"})

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == "Admin":
            try:
                admin_user = AdminUser.objects.get(admin=user, is_active=True)
                company = admin_user.company_id
                requested_company_id = serializer.validated_data.get('company')
                if requested_company_id.id != company:
                    raise serializers.ValidationError("You can only create key points for your own company.")
                
                # Use OpenAI to create key points
                document_content = serializer.validated_data.get('content')
                key_points = self.generate_key_points(document_content)
                serializer.save(added_by=user, content=key_points)
                
            except AdminUser.DoesNotExist:
                raise serializers.ValidationError("Admin user not found.")
        else:
            raise serializers.ValidationError("Only Admins can create document key points.")
    
    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        if (user.role == "Admin" and instance.added_by == user):
            document_content = serializer.validated_data.get('content', instance.content)
            key_points = self.generate_key_points(document_content)
            serializer.save(content=key_points)
            return serializer.data
        else:
            raise serializers.ValidationError("You do not have permission to update these key points.")

    def perform_destroy(self, instance):
        user = self.request.user
        if (user.role == "Admin" and instance.added_by == user):
            # instance.is_active = False
            # instance.save()
            obj_id = instance.id
            instance.delete()
            return Response({"Response":"Successfully Deleted the KeyPoints.","id": obj_id})
        else:
            raise serializers.ValidationError("You do not have permission to delete these key points.")
    
    def generate_key_points(self, content):
        openai.api_key = openai_api_key
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",
            prompt=f"Extract key points from the following document:\n\n{content}",
            max_tokens=150
        )
        key_points = response.choices[0].text.strip()
        return key_points


# class DocumentKeypointsModelViewSet(viewsets.ModelViewSet):
#     queryset = DocumentKeyPoints.objects.all()
#     serializer_class = DocumentKeypointsSerializer
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]
#     filter_backends = [SearchFilter, OrderingFilter]
#     search_fields = ['content', 'prompt_text']


#     def get_queryset(self):
#         return DocumentKeyPoints.objects.filter(company_id=self.request.user.id)

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         document_id = int(request.data['document'])
#         document_keypoint = DocumentKeyPoints.objects.get(document_id = document_id, company_id = self.request.user.id)
#         generateDocumentKeypoints(document_keypoint.id, document_id, serializer.validated_data['prompt_text'])
#         serializer = ReadOnlyDocumentKeypointsSerializer(document_keypoint)

#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)

#         self.perform_update(serializer)
        
        
#         serializer = ReadOnlyDocumentKeypointsSerializer(instance)

#         return Response(serializer.data)
    
#     def list(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())

#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = ReadOnlyDocumentKeypointsSerializer(page, many=True)
#             return self.get_paginated_response(serializer.data)

#         serializer = ReadOnlyDocumentKeypointsSerializer(queryset, many=True)
#         return Response(serializer.data) 

#     def retrieve(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = ReadOnlyDocumentKeypointsSerializer(instance)
#         return Response(serializer.data) 

#     def destroy(self, request, *args, **kwargs):
#         raise serializers.ValidationError("You are not allowed to perform that action.")
