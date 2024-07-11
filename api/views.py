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
openai_api_key =  'sk-proj-5m3pZh3gAS9jirwIgprkT3BlbkFJZOesj9cbny2zc18nvQXo'#'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'
os.environ['OPENAI_API_KEY'] = 'sk-proj-5m3pZh3gAS9jirwIgprkT3BlbkFJZOesj9cbny2zc18nvQXo'#'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'
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
                # print(error)
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
            # print(document.file.path)
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
            company_name = Departments.objects.get(name=name, company=company_id_from_request, is_active=True)
            if company_name:
                raise serializers.ValidationError(
                    {"Department Exists": f"Department with this name {name} already exists in this company"})
        except Departments.DoesNotExist:
            # User does not exist, so continue with user creation
            pass
        # Get the admin user associated with the request user
        if self.request.user.role == 'Admin':
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

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def put(self , request , *args, **kwargs):
        instance = self.get_object()
        admin = AdminUser.objects.get(admin=self.request.user)
        if str(instance.company.id) == str(admin.company.id):
            if admin.is_active==True:
                data = request.data
                new_name = data.get('name')
                if new_name and new_name != instance.name:
                    if Departments.objects.filter(name=new_name, is_active=True).exists():
                        raise serializers.ValidationError({"Error": "A department with this name already exists and is active."})

                serializer = self.get_serializer(instance, data=data, partial=True)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                return Response(serializer.data, status=status.HTTP_200_OK)
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
                
                department_documents = DepartmentsDocuments.objects.filter(department=instance)
                for doc in department_documents:
                    doc.is_active = False  # or doc.delete() to delete
                    doc.save()
                return Response({"Delete Status": "Successfully deleted the department." , "Department_id":instance.id},status=status.HTTP_202_ACCEPTED)
            return Response({"Account Error":"Account did not found"},status=status.HTTP_404_NOT_FOUND)
        return Response({"Account Error":"Your Profile is Not Authorized for this request as you are requesting data for unknown company department."},status=status.HTTP_401_UNAUTHORIZED)

class DepartmentListApiView(ListAPIView):
    serializer_class = DepartmentListSerializers
    queryset = Departments.objects.filter(is_active=True).distinct()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserOrReadOnly]
    
    def get_queryset(self):
        user = self.request.user
        company_id = self.request.query_params.get('company_id')
        if (user.role == 'Admin'):
            admin = AdminUser.objects.get(admin=user)
            if str(company_id) != str(admin.company.id):
                raise serializers.ValidationError({"Permission Denied": "You are not allowed to view departments of this company"})
            if not admin.is_active:
                raise serializers.ValidationError({"Permission Denied": "Your account is restricted. You cannot perform this task"})
            if company_id:
                return Departments.objects.filter(company__id=company_id, is_active=True).distinct()
            return None
            
        elif (user.role == 'Super Admin'):
            if company_id:
                return Departments.objects.filter(company__id=company_id, is_active=True).distinct()
            return None
            
        elif user.role == "User":
            user_id = self.request.query_params.get('user_id', None)
            if not user_id:
                raise serializers.ValidationError({"user_id": "This query parameter is required for users."})

            try:
                user_teams = CompaniesTeam.objects.filter(members=user, is_active=True)
                user_departments = Departments.objects.filter(users__in=user_teams, is_active=True)

                if user_id:
                    user_teams_filtered = CompaniesTeam.objects.filter(id=user_id, members=user, is_active=True)
                    if user_teams_filtered.exists():
                        user_departments = user_departments.filter(users__in=user_teams_filtered).distinct()
                    else:
                        raise serializers.ValidationError({"Permission Denied": "You are not allowed to view departments for this user_id."})
                
                return user_departments
            except CompaniesTeam.DoesNotExist:
                raise serializers.ValidationError({"Permission Denied": "You are not allowed to view departments."}, code="permission_denied")

        else:
            return Response({"Access Denied":"You are Unauthorized"} , status=status.HTTP_401_UNAUTHORIZED)
                    
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


# from openai import OpenAI
import openai
from .serializers import AddUserToDepartmentSerializer
from .permissions import IsAdminUserAndSameCompany

class AddUserToDepartmentView(APIView):
    permission_classes = [IsAdminUserAndSameCompany]

    def post(self, request, *args, **kwargs):
        request_user = self.request.user
        try:
            admin = AdminUser.objects.get(admin=request_user)
        except AdminUser.DoesNotExist:
            return Response({"detail": "Admin user does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        if request_user.role == "Admin" and admin.is_active:
            user_ids = request.data.get('user_ids')
            department_ids = request.data.get('department_ids')

            if not user_ids or not department_ids:
                if not user_ids:
                    return Response({"detail": "User IDs are required."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"detail": "Department IDs are required."}, status=status.HTTP_400_BAD_REQUEST)
            users_not_found = []
            departments_not_found = []
            successfully_added = []

            for user_id in user_ids:
                try:
                    team_member = CompaniesTeam.objects.get(id=user_id , is_active=True)
                except CompaniesTeam.DoesNotExist:
                    users_not_found.append(user_id)
                    continue

                for department_id in department_ids:
                    department = Departments.objects.filter(id=department_id, is_active=True).first()
                    if department:
                        department.users.add(team_member)
                        department.save()
                        successfully_added.append((user_id, department_id))
                    else:
                        departments_not_found.append(department_id)

            response_data = {
                "successfully_added": successfully_added,
                "users_not_found": users_not_found,
                "departments_not_found": departments_not_found,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response({"detail": "Your account is restricted. You cannot perform this task."}, status=status.HTTP_401_UNAUTHORIZED)            
from PyPDF2 import PdfReader
from departments.models import DepartmentsDocuments
from django.shortcuts import get_object_or_404
from documents.models import SummaryCount , KeypointsCount
from .utils import *
import logging
from .serializers import *

logger = logging.getLogger(__name__)

class CreateSummaryApiView(APIView):
    serializer_class = CreateSummarySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = DepartmentsDocuments.objects.filter(is_active=True)

    def get(self, request):
        document_id = request.query_params.get('document_id')
        if not document_id:
            return Response({"error": "document_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            document = DepartmentsDocuments.objects.get(id=document_id, is_active=True)
        except DepartmentsDocuments.DoesNotExist:
            return Response({"error": "No Document Found"}, status=status.HTTP_404_NOT_FOUND)
        
        user = request.user
        
        if user.role == "Super Admin":
            pass
        elif user.role == "Admin":
            admin = AdminUser.objects.get(admin=user)
            if admin.is_active == True:
                if str(admin.company.id) != str(document.department.company.id):
                    return Response({"Access Denied":"You are not allowed to view the summary of this document"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                raise serializers.ValidationError({"Unauthorized": "You are blocked or deleted"})
        elif user.role == "User":
            member = CompaniesTeam.objects.filter(members=user).first()
            if member.is_active == True:
                user_departments = Departments.objects.filter(users=member, is_active=True)
                if not user_departments.exists():
                    return Response({"No Association": "You are no longer associated with this department"}, status=status.HTTP_403_FORBIDDEN)
            else:
                raise serializers.ValidationError({"Unauthorized": "You are blocked or deleted"})
            if not user_departments.filter(id=document.department.id).exists():
                return Response({"Access Denied": "You are not allowed to view the summary of this department"}, status=status.HTTP_403_FORBIDDEN)
        try:
            summary = DocumentSummary.objects.filter(document=document).first()
            if not summary:
                return Response({"Not Found":"No Summary Found against this document."}, status = status.HTTP_404_NOT_FOUND)
            if user.role == 'User':
                return Response({"id": summary.id, "summary": summary.summary}, status=status.HTTP_200_OK)
            return Response({"id": summary.id, "summary": summary.summary, "prompt":summary.prompt}, status=status.HTTP_200_OK)

        except DocumentSummary.DoesNotExist:
            return Response({"error": "No summary found for this document"}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self , request):
        if request.user.role == "Admin":
            document_id = request.data.get('document')
            prompt = request.data.get('prompt')
            if not document_id:
                return Response({"error":"document is required"}, status=status.HTTP_400_BAD_REQUEST)        
            
            user = request.user        
                
            try:
                document = DepartmentsDocuments.objects.get(id=document_id, is_active=True)
            except DepartmentsDocuments.DoesNotExist:
                return Response({"error":"No Document Found"}, status=status.HTTP_404_NOT_FOUND)

            if user.role == "Admin":
                admin = AdminUser.objects.get(admin=user, is_active=True)
                if admin.is_active == True:
                    if str(admin.company.id) != str(document.department.company.id):
                        return Response({"Access Denied":"You are not allowed to create the summary of this document"}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    raise serializers.ValidationError({"Unauthorized": "You are blocked or deleted"})
            if not document.file:
                return Response({"Not Found":"No File is associated"}, status=status.HTTP_400_BAD_REQUEST)

            summary_request = DocumentSummary.objects.filter(document=document, added_by=user).count()
            if summary_request == 5:
                return Response({"error": "Summary creation limit reached. No more than 5 requests allowed for this document."}, status=status.HTTP_403_FORBIDDEN)

            content = read_file_content(document.file)
            
            if content is None:
                return Response({"error": "Unable to decode file content"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if not content.strip():
                logger.error("Decoded content is empty")
                return Response({"error": "Decoded content is empty"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            logger.info(f"Decoded content: {content[:100]}")  # Log the first 100 characters of the content

            try:
                summary , _ = generate_summary_from_gpt(content , prompt)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            created_summary = DocumentSummary.objects.create(
                summary=summary,
                document = document,
                prompt = _ ,
                added_by = self.request.user                
            ) 
            
            # summary_request.request_count += 1
            # summary_request.save()
            
            return Response({"id":created_summary.id , "summary":f"{created_summary.summary}", "prompt":f"{created_summary.prompt}"}, status=status.HTTP_200_OK)
        return Response({"Access Denied":"You Are not Allowed to create summary"}, status=status.HTTP_401_UNAUTHORIZED)

class CreateKeypointsApiView(APIView):
    serializer_class = CreateKeypointsSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = DepartmentsDocuments.objects.filter(is_active=True)

    def get(self, request):
        document_id = request.query_params.get('document_id')
        if not document_id:
            return Response({"error": "document_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            document = DepartmentsDocuments.objects.get(id=document_id, is_active=True)
        except DepartmentsDocuments.DoesNotExist:
            return Response({"error": "No Document Found"}, status=status.HTTP_404_NOT_FOUND)
        
        user = request.user
        
        if user.role == "Super Admin":
            pass
        elif user.role == "Admin":
            admin = AdminUser.objects.get(admin=user)
            if admin.is_active == True:
                if str(admin.company.id) != str(document.department.company.id):
                    return Response({"Access Denied":"You are not allowed to view the summary of this document"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                raise serializers.ValidationError({"Unauthorized": "You are blocked or deleted"})
        elif user.role == "User":
            member = CompaniesTeam.objects.filter(members=user).first()
            if member.is_active == True:
                user_departments = Departments.objects.filter(users=member, is_active=True)
                if not user_departments.exists():
                    return Response({"No Association": "You are no longer associated with this department"}, status=status.HTTP_403_FORBIDDEN)
            else:
                raise serializers.ValidationError({"Unauthorized": "You are blocked or deleted"})
            if not user_departments.filter(id=document.department.id).exists():
                return Response({"Access Denied": "You are not allowed to view the summary of this department"}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            keypoints = DocumentKeyPoints.objects.filter(document=document).first()
            if user.role == 'User':
                return Response({"id": keypoints.id, "keypoints": keypoints.keypoints}, status=status.HTTP_200_OK)
            return Response({"id": keypoints.id, "keypoints": keypoints.keypoints, "prompt":keypoints.prompt}, status=status.HTTP_200_OK)            
        except DocumentSummary.DoesNotExist:
            return Response({"error": "No keypoints found for this document"}, status=status.HTTP_404_NOT_FOUND)

    def post(self , request):
        if request.user.role == "Admin":
            document_id = request.data.get('document')
            prompt = request.data.get('prompt')
            if not document_id:
                return Response({"error":"document is required"}, status=status.HTTP_400_BAD_REQUEST)        
            
            try:
                document = DepartmentsDocuments.objects.get(id=document_id, is_active=True)
            except DepartmentsDocuments.DoesNotExist:
                return Response({"error":"No Document Found"}, status=status.HTTP_404_NOT_FOUND)

            user = request.user

            if user.role == "Admin":
                admin = AdminUser.objects.get(admin=user)
                if admin.is_active == True:
                    if str(admin.company.id) != str(document.department.company.id):
                        return Response({"Access Denied":"You are not allowed to create the summary of this document"}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    raise serializers.ValidationError({"Unauthorized": "You are blocked or deleted"})

            if not document.file:
                return Response({"Not Found":"No File is associated"}, status=status.HTTP_400_BAD_REQUEST)

            keypoint_count = DocumentKeyPoints.objects.filter(document=document , added_by=user).count()
            # keypoints_request, created = KeypointsCount.objects.get_or_create(admin=admin, document=document)
            if keypoint_count == 5:
                return Response({"error": "Keypoints creation limit reached. No more than 5 requests allowed for this document."}, status=status.HTTP_403_FORBIDDEN)

            content = read_file_content(document.file)
            
            if content is None:
                return Response({"error": "Unable to decode file content"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if not content.strip():
                logger.error("Decoded content is empty")
                return Response({"error": "Decoded content is empty"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            logger.info(f"Decoded content: {content[:100]}")  # Log the first 100 characters of the content

            try:
                keypoints , _ = generate_keypoints_from_gpt(content, prompt)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            created_keypoint = DocumentKeyPoints.objects.create(
                keypoints=keypoints,
                prompt = _ ,
                document = document,
                added_by = self.request.user                
            ) 
            
            # keypoints_request.request_count += 1
            # keypoints_request.save()
            
            return Response({"id":created_keypoint.id , "keypoints":f"{created_keypoint.keypoints}", "prompt":f"{created_keypoint.prompt}"}, status=status.HTTP_200_OK)
        return Response({"Access Denied":"You Are not Allowed to create keypoints"}, status=status.HTTP_401_UNAUTHORIZED)

from documents.models import QuizQuestions , QuizResult

import json


class QuestionsofQuiz(ListAPIView):
    serializer_class = QuizQuestionsListSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserOrReadOnly]
    def get_queryset(self):
        quiz_id = self.request.query_params.get('quiz_id')
        if not quiz_id:
            return QuizQuestions.objects.none()
        
        quiz = get_object_or_404(DocumentQuiz, id=quiz_id)
        questions = QuizQuestions.objects.filter(quiz=quiz)
        return questions

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)    


#nsm
class QuizResultsApiView(APIView):    
    def get(self, request):
        if request.user.role == "User":
            return Response({"Access Denied":"You are not allowed to view the data"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            quiz_id = request.query_params.get('quiz_id')  # Retrieve quiz_id from query parameters
            
            if not quiz_id:
                return Response({"error": "quiz_id is required"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                quiz = DocumentQuiz.objects.get(id=quiz_id)
            except DocumentQuiz.DoesNotExist:
                return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

            quiz_results = QuizResult.objects.filter(quiz=quiz)
            if not quiz_results:
                return Response({"error": "No results found for this quiz"}, status=status.HTTP_404_NOT_FOUND)

            response_data = []
            for result in quiz_results:
                user = result.user.members
                response_data.append({
                    "user_id": user.id,
                    "user_name": user.get_full_name(),
                    "score": result.score,
                    "status": result.status
                })

            return Response(response_data, status=status.HTTP_200_OK)

from django.core.exceptions import PermissionDenied
class CreateQuizessApiView(APIView):
    serializer_class = CreateQuizesSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = DepartmentsDocuments.objects.filter(is_active=True)

    def get(self, request):
        document_id = request.query_params.get('document_id')
        if not document_id:
            return Response({"error": "document_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            document = DepartmentsDocuments.objects.get(id=document_id, is_active=True)
        except DepartmentsDocuments.DoesNotExist:
            return Response({"error": "No Document Found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        if user.role == "Super Admin":
            quizzes = DocumentQuiz.objects.filter(document=document)
        elif user.role == "Admin":
            admin = AdminUser.objects.get(admin=user)
            if admin.is_active:
                if str(admin.company.id) == str(document.department.company.id):
                    quizzes = DocumentQuiz.objects.filter(document=document)
                else:
                    return Response({"Access Denied": "You are not allowed to view quizzes for this document"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                raise serializers.ValidationError({"Unauthorized": "You are blocked or deleted"})
        else:  # Regular User
            member = CompaniesTeam.objects.filter(members=user).first()
            if member and member.is_active:
                assigned_documents = DepartmentsDocuments.objects.filter(department__users=member, is_active=True)
                if document in assigned_documents:
                    quizzes = DocumentQuiz.objects.filter(document=document, upload=True)
                else:
                    return Response({"Access Denied": "You are not allowed to view quizzes for this document"}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({"No Association": "You are no longer associated with this department"}, status=status.HTTP_403_FORBIDDEN)

        # Prepare the response data
        if request.user.role == 'User':
            response_data = []
            for quiz in quizzes:
                # Check if the user has already attempted the quiz
                try:
                    quiz_result = QuizResult.objects.get(user=member, quiz=quiz)
                    quiz_data = {
                        "id": quiz.id,
                        "name": quiz.name,
                        "upload_status": quiz.upload,
                        "attempt_status": "Attempted",
                        "score": quiz_result.score,
                        "result_status": quiz_result.status
                    }
                except QuizResult.DoesNotExist:
                    quiz_data = {
                        "id": quiz.id,
                        "name": quiz.name,
                        "upload_status": quiz.upload,
                        "attempt_status": "Yet to attempt",
                        "score": None,
                        "result_status": None
                    }
                response_data.append(quiz_data)

            return Response(response_data, status=status.HTTP_200_OK)    
        else:
            response_data = []
            for quiz in quizzes:
                # Check if the user has already attempted the quiz
                quiz_data = {
                        "id": quiz.id,
                        "name": quiz.name,
                        "upload_status": quiz.upload,
                }
                response_data.append(quiz_data)
            return Response(response_data, status=status.HTTP_200_OK)


    def post(self , request):
        if request.user.role == "Admin":
            document_id = request.data.get('document')
            if not document_id:
                return Response({"error":"document is required"}, status=status.HTTP_400_BAD_REQUEST)        
            
            try:
                document = DepartmentsDocuments.objects.get(id=document_id, is_active=True)
            except DepartmentsDocuments.DoesNotExist:
                return Response({"error":"No Document Found"}, status=status.HTTP_404_NOT_FOUND)

            user = request.user

            if user.role == "Admin":
                admin = AdminUser.objects.get(admin=user)
                if admin.is_active == True:
                    if str(admin.company.id) != str(document.department.company.id):
                        return Response({"Access Denied":"You are not allowed to create the Quiz of this document"}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    raise serializers.ValidationError({"Unauthorized": "You are blocked or deleted"})

            if not document.file:
                return Response({"Not Found":"No File is associated"}, status=status.HTTP_400_BAD_REQUEST)

            quiz_count = DocumentQuiz.objects.filter(document=document, added_by=user).count()
            if quiz_count >= 10:
                return Response({"error": "Quiz creation limit reached. No more than 10 quizzes allowed for this document."}, status=status.HTTP_403_FORBIDDEN)

            content = read_file_content(document.file)
            
            if content is None:
                return Response({"error": "Unable to decode file content"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if not content.strip():
                logger.error("Decoded content is empty")
                return Response({"error": "Decoded content is empty"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            logger.info(f"Decoded content: {content[:100]}")  # Log the first 100 characters of the content

            try:
                quiz , _ = generate_quizes_from_gpt(content)
                if quiz is None:
                    return Response({"error": "Failed to generate quiz"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            created_quiz = DocumentQuiz.objects.create(
                name= f"Quiz # {quiz_count} of {document.name}",
                quiz=quiz,
                prompt = _ ,
                document = document,
                added_by = self.request.user                
            ) 
            
            # response_data = json.loads(quiz)
            
            # questions_data = quiz.split("Question:")

            possible_formats = ["Question:", "question:", "Question 1:", "q:"]
            questions_data = []
            temp_data = quiz
            for fmt in possible_formats:
                if fmt in temp_data:
                    parts = temp_data.split(fmt)
                    if len(parts) > 1:
                        questions_data.extend(parts[1:])
                        temp_data = parts[0]

            if len(questions_data) - 1 > 10:
                return Response({"error": "Each quiz can have a maximum of 10 questions."}, status=status.HTTP_400_BAD_REQUEST)

            

            # Iterate through the questions and create QuizQuestions objects
            for question_data in questions_data[1:]:
                lines = question_data.strip().split("\n")

                # Extract question text
                question_text = lines[0].strip()

                # Extract options and correct answer
                options = {}
                correct_answer = None
                for line in lines[1:]:
                    parts = line.split(": ")
                    if len(parts) >= 2:  # Check if there are at least two elements
                        option = parts[0].strip()
                        text = parts[1].strip()
                        if parts[0].strip() == "Correct Answer":
                            correct_answer = parts[1].strip()
                            # print(correct_answer)
                        options[option] = text
                # Create QuizQuestions object
                quiz_question = QuizQuestions.objects.create(
                    question=question_text,
                    option_1=options.get("A"),
                    option_2=options.get("B"),
                    option_3=options.get("C"),
                    option_4=options.get("D"),
                    answer=correct_answer,
                    quiz=created_quiz,  # Assuming 'created_quiz' is the instance of DocumentQuiz created earlier
                    added_by=request.user  # Assuming 'request' is available in this context "prompt":f"{created_quiz.prompt}"
                )
            return Response({"id":created_quiz.id , "quiz":f"{created_quiz.quiz}"}, status=status.HTTP_200_OK)
        return Response({"Access Denied":"You Are not Allowed to create quiz"}, status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, quiz_id):
        try:
            if request.user.role == 'Admin':
                if not quiz_id:
                    return Response({"error": "quiz_id is required"}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    quiz = DocumentQuiz.objects.get(id=quiz_id)
                except DocumentQuiz.DoesNotExist:
                    return Response({"error": "No Quiz Found"}, status=status.HTTP_404_NOT_FOUND)

                admin = AdminUser.objects.get(admin=request.user)
                if not admin.is_active:
                    raise serializers.ValidationError({"Unauthorized": "You are blocked or deleted"})
                if str(admin.company.id) != str(quiz.document.department.company.id):
                    return Response({"Access Denied": "You are not allowed to delete this quiz"}, status=status.HTTP_401_UNAUTHORIZED)

                quiz.delete()
                logger.info(f"Quiz with id {quiz.id} deleted successfully by {request.user.id}")
                return Response({"message": "Quiz deleted successfully", "id": quiz_id}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"Access Denied": "You are not allowed to delete quizzes"}, status=status.HTTP_401_UNAUTHORIZED)
        except serializers.ValidationError as e:
            logger.error(f"Validation error: {e.detail}")
            return Response(e.detail, status=status.HTTP_403_FORBIDDEN)
        except PermissionDenied as e:
            logger.error(f"Permission denied: {str(e)}")
            return Response({"Access Denied": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"Internal server error: {str(e)}", exc_info=True)
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteQuizApiView(DestroyAPIView):
    serializer_class = CreateQuizesSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = DocumentQuiz.objects.all()
    lookup_field = 'id'
    
    def destroy(self):
        quiz = self.get_object()
        id = DocumentQuiz.objects.filter(id=quiz)
        quiz.delete()
        return Response({"Delete Message":"Quiz Deleted Successfully" , "id": id.id} , status=status.HTTP_200_OK)
    
class UploadQuiz(APIView):
    serializer_class = CreateQuizesSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = DocumentQuiz.objects.all()
    
    def post(self , request):
        quiz_id = request.data.get('quiz_id')
        quiz = DocumentQuiz.objects.get(id=quiz_id)
        if quiz:
            quiz.upload = True
            quiz.save()
            return Response({"message":"Quiz is Successfully uploaded or updated", "id":quiz.id}, status=status.HTTP_202_ACCEPTED)
        return Response({"Not Found":"No quiz found"}, status=status.HTTP_404_NOT_FOUND)

class EditQuizes(APIView):
    serializer_class = QuizQuestionsSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserOrReadOnly]

    def put(self, request, question_id):
        return self.update_question(request, question_id, partial=False)

    def patch(self, request, question_id):
        return self.update_question(request, question_id, partial=True)

    def update_question(self, request, question_id, partial):
        question = get_object_or_404(QuizQuestions, id=question_id)
        user = request.user

        if user.role != "Admin":
            return Response({"error": "Access Denied"}, status=status.HTTP_403_FORBIDDEN)

        admin = AdminUser.objects.get(admin=user)
        if not admin.is_active:
            raise serializers.ValidationError({"Unauthorized": "You are blocked or deleted"})
        if str(admin.company.id) != str(question.quiz.document.department.company.id):
            return Response({"Access Denied": "You are not allowed to edit this question"}, status=status.HTTP_403_FORBIDDEN)

        # Ensure that options is a list of dictionaries
        options = request.data.get('options')
        if options and isinstance(options, list) and len(options) == 1 and isinstance(options[0], dict):
            options_dict = options[0]
            question.option_1 = options_dict.get('A')
            question.option_2 = options_dict.get('B')
            question.option_3 = options_dict.get('C')
            question.option_4 = options_dict.get('D')
            del request.data['options']  # Remove options from request data to avoid conflict
        elif options:
            return Response({"error": "Invalid options format"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(question, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def put(self, request, question_id):
    #     question = get_object_or_404(QuizQuestions, id=question_id)
    #     user = request.user

    #     if user.role != "Admin":
    #         return Response({"error": "Access Denied"}, status=status.HTTP_403_FORBIDDEN)

    #     admin = AdminUser.objects.get(admin=user)
    #     if not admin.is_active:
    #         raise serializers.ValidationError({"Unauthorized": "You are blocked or deleted"})
    #     if str(admin.company.id) != str(question.quiz.document.department.company.id):
    #         return Response({"Access Denied": "You are not allowed to edit this question"}, status=status.HTTP_403_FORBIDDEN)

    #     serializer = self.serializer_class(question, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, question_id):
        question = get_object_or_404(QuizQuestions, id=question_id)
        user = request.user

        if user.role != "Admin":
            return Response({"error": "Access Denied"}, status=status.HTTP_403_FORBIDDEN)

        admin = AdminUser.objects.get(admin=user)
        if not admin.is_active:
            raise serializers.ValidationError({"Unauthorized": "You are blocked or deleted"})
        if str(admin.company.id) != str(question.quiz.document.department.company.id):
            return Response({"Access Denied": "You are not allowed to delete this question"}, status=status.HTTP_403_FORBIDDEN)
        q_id = question.id
        question.delete()
        return Response({"message": "Question deleted successfully", "id":q_id}, status=status.HTTP_200_OK)

from .permissions import IsAssociatedWithDepartment

class SubmitQuizView(APIView):
    # permission_classes = [IsAssociatedWithDepartment]
    def post(self, request):
        if request.user.role == "Admin" or request.user.role == "Super Admin":
            return Response({"Access Denied":"You are not authorized for this request"} , status = status.HTTP_401_UNAUTHORIZED)
        elif request.user.role == "User":
            member = CompaniesTeam.objects.filter(members=request.user).first()
            if member.is_active==True:
                user_departments = Departments.objects.filter(users=member, is_active=True)
                if not user_departments.exists():
                    return Response({"Not Found":"Department Not Found"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                raise serializers.ValidationError({"Unauthorized": "You are blocked or deleted"})
            quiz_id = request.data.get("quiz_id")
            document = DocumentQuiz.objects.filter(id=quiz_id).first()
            
            if not document:
                return Response({"Not Found": "Document Not Found"}, status=status.HTTP_404_NOT_FOUND)
            
            document_department = document.document.department

            if not user_departments.filter(id=document_department.id).exists():
                return Response({"Access Denied": "You are not allowed to submit quiz for this document"}, status=status.HTTP_403_FORBIDDEN)

            answers = request.data.get("answers", [])

            # Fetch the quiz questions for the provided quiz_id
            quiz_questions = QuizQuestions.objects.filter(quiz_id=quiz_id)

            if not quiz_questions.exists():
                return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

            # Validate the answers
            total_questions = len(quiz_questions)
            correct_answers = 0
            for answer_data in answers:
                question_id = answer_data.get("question_id")
                selected_option = answer_data.get("option")

                # Fetch the question from the database
                try:
                    question = quiz_questions.get(id=question_id)
                except QuizQuestions.DoesNotExist:
                    return Response({"error": f"Question with id {question_id} not found in the quiz"}, status=status.HTTP_404_NOT_FOUND)

                # Check if the selected option is correct
                if question.answer == selected_option:
                    correct_answers += 1

            # Calculate the score
            score = (correct_answers / total_questions) * 100

            if score > 33:
                status_test = "Pass"
            else:
                status_test = "Fail"
            member = CompaniesTeam.objects.filter(members=request.user).first()
            quiz_result, created = QuizResult.objects.update_or_create(
                user=member,
                quiz=document,
                defaults={'score': score, 'status': status_test}
            )
            
            return Response({"Score": score , "Status":status_test}, status=status.HTTP_200_OK)
        else:
            return Response({"Access Denied":"Unauthorized Access Requested"}, status=status.HTTP_401_UNAUTHORIZED)

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
                document_id = self.request.data.get('document')
                prompt_text = self.request.data.get('prompt_text', "Summarize the following document:")
                admin_user = AdminUser.objects.get(admin=user, is_active=True)
                company = admin_user.company_id
                requested_company_id = self.request.data.get('company')
                print(company)
                print(requested_company_id)
                print(str(requested_company_id) != str(company))
                if str(requested_company_id) != str(company):
                    raise serializers.ValidationError("You can only create summaries for your own company.")
                
                
                # document_id = serializer.validated_data.get('document')
                print(document_id)
                document = get_object_or_404(DepartmentsDocuments, id=document_id)
                document_content = self.extract_document_content(document)
                max_input_tokens = 2048  # Example limit
                truncated_content = self.truncate_content(document_content, max_input_tokens)
                # Now you have the document content, use it to generate the summary
                summary = self.generate_summary(truncated_content, prompt_text)
                # file_data = document.file.read()
                # print(file_data)
                # document = DepartmentsDocuments.objects.get(id=document_id, is_active=True)
                
                # Use OpenAI to create summary
                summary = self.generate_summary(truncated_content, prompt_text)
                serializer = DocumentSummarySerializer(data={
                    'content': summary,
                    'company': requested_company_id,
                    'document': document_id,
                    'prompt_text': prompt_text
                })
                if serializer.is_valid():
                    serializer.save(added_by=self.request.user)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                
            except AdminUser.DoesNotExist:
                raise serializers.ValidationError("Admin user not found.")
            except DepartmentsDocuments.DoesNotExist:
                raise serializers.ValidationError("Document not found or is not active.")
        else:
            raise serializers.ValidationError("Only Admins can create document summaries.")

    
    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        if (user.role == "Admin" and instance.added_by == user):
            document_id = serializer.validated_data.get('document', instance.document.id)
            document = DepartmentsDocuments.objects.get(id=document_id)
            document_content = self.extract_document_content(document)
            summary = self.generate_summary(document_content)
            serializer.save(content=document_content, summary=summary)
            return serializer.data
        else:
            raise serializers.ValidationError("You do not have permission to update this summary.")

    def truncate_content(self, content, max_tokens):
        # Implement your token counting logic here
        # This is a simple example that cuts off the content at max_tokens characters
        if len(content) > max_tokens:
            return content[:max_tokens]
        return content

    def generate_summary(self, content, prompt_text):
        openai.api_key = openai_api_key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{prompt_text}\n\n{content}"}
            ],
            max_tokens=150  # Adjust this as necessary
        )
        summary = response.choices[0].message['content'].strip()
        return summary

    def extract_document_content(self, document):
        if document.file.name.endswith('.pdf'):
            with document.file.open('rb') as file:
                reader = PdfReader(file)
                content = ""
                for page in reader.pages:
                    content += page.extract_text()
                return content
        elif document.file.name.endswith('.txt'):
            with document.file.open('r') as file:
                return file.read()
        else:
            raise serializers.ValidationError("Unsupported file format.")

    def perform_destroy(self, instance):
        user = self.request.user
        if (user.role == "Admin" and instance.added_by == user):
            obj_id = instance.id
            instance.delete()
            return Response({"Response":"Successfully Deleted the Summary.","id": obj_id})
        else:
            raise serializers.ValidationError("You do not have permission to delete this summary.")
