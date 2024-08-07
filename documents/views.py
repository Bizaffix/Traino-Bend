from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from departments.models import DepartmentsDocuments , Departments
from .serializers import DepartmentsDocumentsSerializer, DepartmentsDocumentsCreateSerializer
from teams.models import CompaniesTeam 
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminUserOrReadOnly, IsAdminUserOfCompany
from rest_framework_simplejwt.authentication import JWTAuthentication
from company.models import AdminUser
from django.shortcuts import render
from django.http import JsonResponse
from langchain_community.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain_community.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import PyPDFLoader
from .models import QuizQuestions, DocumentQuiz, DocumentTeam
from rest_framework.generics import *
from PyPDF2 import PdfReader
from langchain.prompts import PromptTemplate
import os
import json
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.contrib import messages
from departments.models import DepartmentsDocuments
from dotenv import load_dotenv
load_dotenv()
openai_api_key= os.getenv('OPENAI_API_KEY')

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

# Create your views here.
def generateDocumentSummary(request):
    data = {'document_summary': '', 'msg': ''}
    if request.method == 'POST':
        document_id = request.POST.get('document_id')
        prompt_text = request.POST.get('prompt_text')
        data['document_id'] = document_id
        data['prompt_text'] = prompt_text
        if document_id == 0 or document_id is None:
            data['msg'] = 'Please select document to generate summary'
        elif prompt_text == '' or prompt_text is None:
            data['msg'] = 'Please enter prompt text to generate summary'
        else:
            data['document_summary'] = 'Oops! Summary not generated please try with some other document.'

            document = DepartmentsDocuments.objects.get(id=document_id)
            if document.file.path is not None:
                try:
                    print("test: 1")
                    llm = ChatOpenAI(model_name='gpt-3.5-turbo')
                    print("test: 2")
                    print(document.file.path)

                    loader = PyPDFLoader(document.file.path)
                 
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
                            chunk_size=1000,
                            chunk_overlap=100
                        )
                    # print(text_splitter)
                    
                    #create_documents() create documents froma list of texts
                    
                    text = text_splitter.create_documents([text])
                    # print(len(docs))
                    # print(docs)

                    print("test: 4")

                    # Define prompt
                    prompt_template = """You are required to generate """+prompt_text+""" based on the provided text:
                    {text}
                    CONCISE SUMMARY:"""

                    

                    prompt_template = PromptTemplate(template=prompt_template, input_variables=["text"])

                    # Text summarization
                    chain = load_summarize_chain(llm, chain_type='stuff', prompt=prompt_template)
                    print("test: 5")
                    data['document_summary'] = chain.run(text)
                    print("test: 6")
                except Exception as error:
                    if error.code == 'insufficient_quota':
                        data['msg'] = 'You exceeded your current quota, please check your plan and billing details.'
                    else:
                        data['msg'] = 'Your document content is too large, Please try with some other document.'
                    print(error)
    return JsonResponse(data, status=200)

def generateDocumentKeypoints(request):
    data = {'document_keypoints': '', 'msg': ''}
    if request.method == 'POST':
        document_id = request.POST.get('document_id')
        prompt_text = request.POST.get('prompt_text')
        data['document_id'] = document_id
        data['prompt_text'] = prompt_text
        if document_id == 0 or document_id is None:
            data['msg'] = 'Please select document to generate keypoints'
        elif prompt_text == '' or prompt_text is None:
            data['msg'] = 'Please enter prompt text to generate keypoints'
        else:
            data['document_keypoints'] = 'Oops! Keypoints not generated please try with some other document.'

            document = DepartmentsDocuments.objects.get(id=document_id)
            if document.file.path is not None:
                try:
            
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
                    data['document_keypoints'] = chain.run(text)
                    #print(len(data['document_keypoints']))
                    #print(data['document_keypoints'])
                    #print("test: 6")
                except Exception as error:
                    if error.code == 'insufficient_quota':
                        data['msg'] = 'You exceeded your current quota, please check your plan and billing details.'
                    else:
                        data['msg'] = 'Your document content is too large, Please try with some other document.'
                    print(error)
    return JsonResponse(data, status=200)

def saveDocumentTeam(request, document_id):
    if request.method == 'POST':

        doc_team_ids = request.POST.get('doc_team_ids')
        
        if(doc_team_ids is not None):
            doc_team_ids = doc_team_ids.split(',')
            for doc_team_id in doc_team_ids:
                is_assigned = request.POST.get('assigned_'+doc_team_id+"_options")
                notify_frequency = request.POST.get('frequency_'+doc_team_id)
                doc_team = DocumentTeam.objects.get(id=doc_team_id)
                if doc_team is not None:
                    doc_team.is_assigned = is_assigned
                    doc_team.notify_frequency = notify_frequency
                    doc_team.save()
            messages.success(request, "Document team(s) updated.")

    return redirect("/admin/documents/userdocuments/"+str(document_id)+"/viewTeam")

def publishDocument(request):
    data = {'label': '', 'msg': ''}
    if request.method == 'POST':
        document_id = request.POST.get('document_id')
        company_document = DepartmentsDocuments.objects.get(id=document_id)
        if company_document is not None and company_document.published is True:
            company_document.published = False
            company_document.save()
            data['label'] = 'Make Publish'
        elif company_document is not None and company_document.published is False:
            company_document.published = True
            company_document.save()
            data['label'] = 'Make Unpublish'
    return JsonResponse(data, status=200)

def deleteQuizQuestion(request, question_id):
    data = {'status': 0, 'msg': ''}
    if request.method == 'POST':
        quiz_question = QuizQuestions.objects.get(id=question_id)
        if quiz_question is not None:
            quiz_question.delete()
            data['status'] = 1
    return JsonResponse(data, status=200)

def attemptQuiz(request, quiz_id):
    correct_answers = 0
    wrong_answers = 0
    total_questions = 0
    total_score = 0
    result_status = 'Fail'
    if request.method == 'POST':

        question_ids = request.POST.get('question_ids')
        
        if(question_ids is not None):
            question_ids = question_ids.split(',')
            for question_id in question_ids:
                answer = request.POST.get('question_'+question_id+"_options")
                q_question = QuizQuestions.objects.get(id = int(question_id))
                if answer == q_question.answer:
                    correct_answers += 1
                else:
                    wrong_answers += 1
            

            total_questions = correct_answers + wrong_answers
            total_score = float("{:.2f}".format(((correct_answers/total_questions)*100)))
            print(total_score)
            if total_score >= 75.00:
                result_status = 'Pass'

    return redirect("/admin/documents/documentquiz/"+str(quiz_id)+"/quizResult?cq="+str(correct_answers)+"&wq="+str(wrong_answers)+"&tq="+str(total_questions)+"&ts="+str(total_score)+"&rs="+str(result_status))

def generateDocumentQuiz(request):
    data = {'document_keypoints': '', 'msg': ''}
    if request.method == 'POST':
        document_id = request.POST.get('document_id')
        quiz_id = request.POST.get('quiz_id')
        prompt_text = request.POST.get('prompt_text')
        data['document_id'] = document_id
        data['prompt_text'] = prompt_text
        if document_id == 0 or document_id is None:
            data['msg'] = 'Please select document to generate quiz'
        elif prompt_text == '' or prompt_text is None:
            data['msg'] = 'Please enter prompt text to generate quiz'
        else:
            data['document_keypoints'] = 'Oops! Quiz not generated please try with some other document.'

            document = DepartmentsDocuments.objects.get(id=document_id)
            if document.file.path is not None:
                try:
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
                    # prompt_template = """You are required to generate """+prompt_text+""" based on the provided text:
                    # {text}
                    # CONCISE OUTLINE:"""

                    # prompt_template = """You are required to generate 25 multiple choice questions having four options and correct answer in json format based on the provided text:
                    # {text}
                    # MCQ QUIZ:"""

                    prompt_template = """You are a teacher preparing questions for a quiz. Based on the following document, please generate upto """+prompt_text+""" with four options and a correct answer. Follow below example format and convert result to json array of objects:
                    
                    Example question:
                    
                    question:question here
                    options:option 1, option 2, option 3, option 4
                    answer:0 or 1 or 2 or 3
                    
                    <Begin Document>
                    {text}
                    <End Document>
                    MCQ QUIZ:"""

                    prompt_template = PromptTemplate(template=prompt_template, input_variables=["text"])

                    

                    # Text summarization
                    chain = load_summarize_chain(llm, chain_type='stuff', prompt=prompt_template)
                    #print("test: 5")
                    document_quiz = chain.run(text)
                    # print(len(document_quiz))
                    # print(document_quiz)
                    # print("test: 6")
                    if(document_quiz.endswith(']') == False):
                        quiz_array = document_quiz.split('},')
                        quiz_array.pop((len(quiz_array) - 1))
                        document_quiz = '},'.join(quiz_array)
                        document_quiz = document_quiz + '}]'
                    # print(document_quiz)
                    # print("test: 7")
                    document_quiz = json.loads(document_quiz)
                    try:
                        dquiz = QuizQuestions.objects.filter(quiz_id = int(quiz_id) ).delete() 
                    except QuizQuestions.DoesNotExist:
                        dquiz = None
                    # for quiz in document_quiz:
                    #     if(quiz['question'] is not None and quiz['options'] is not None and quiz['answer'] is not None):
                    #         q_question = QuizQuestions(question = quiz['question'], option_1 = quiz['options'][0], option_2 = quiz['options'][1], option_3 = quiz['options'][2], option_4 = quiz['options'][3], answer = quiz['answer'], quiz_id = quiz_id, document_id = document_id)
                    #         q_question.save()

                    # print(document_quiz[0]['question'])
                    # print(document_quiz[0]['options'])
                    # print(document_quiz[0]['answer'])
                    data['document_quiz'] = json.dumps(document_quiz, indent=4)
                except Exception as error:
                    if error.code == 'insufficient_quota':
                        data['msg'] = 'You exceeded your current quota, please check your plan and billing details.'
                    else:
                        data['msg'] = 'Your document content is too large, Please try with some other document.'
                    print(error)
    return JsonResponse(data, status=200)


from django.utils import timezone
from .tasks import upload_document

class DepartmentsDocumentsCreateAPIView(generics.CreateAPIView):
    queryset = DepartmentsDocuments.objects.filter(is_active=True)
    serializer_class = DepartmentsDocumentsCreateSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    authentication_classes = [JWTAuthentication]

    def perform_create(self, serializer):
        documents = serializer.save(added_by=self.request.user)
        return documents

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        department_ids = validated_data.pop('department_ids')
        user_ids = validated_data.pop('user_ids', [])
        all_users = validated_data.pop('all', False)
        name = validated_data['name']
        # print(all_users)
        failure_departments = []
        created_documents = []
        
        for department_id in department_ids:
            try:
                department = Departments.objects.get(id=department_id, is_active=True)
            except Departments.DoesNotExist:
                continue  # Skip invalid departments

            existing_document = DepartmentsDocuments.objects.filter(name=name, department=department, is_active=True).exists()
            if existing_document:
                failure_departments.append(department_id)
            else:
                document = DepartmentsDocuments.objects.create(
                    name=name,
                    added_by=request.user,
                    file=validated_data['file'],
                    department=department,
                    published=validated_data.get('published', False)
                )
                valid_team_ids = []
                
                if all_users:
                    assigned_users = CompaniesTeam.objects.filter(departments__id=department_id)
                    # print(assigned_users)
                    # document.assigned_users.set(assigned_users)
                else:
                    valid_team_ids = []
                    for user_id in user_ids:
                        if department.users.filter(id=user_id, is_active=True).exists():
                            valid_team_ids.append(user_id)
                    assigned_users = CompaniesTeam.objects.filter(id__in=valid_team_ids)
                    # print(assigned_users)
                    # document.assigned_users.set(assigned_users)
                
                document.assigned_users.set(assigned_users)
                created_documents.append(document.id)

        if sorted(failure_departments) == sorted(department_ids):
            failure_message = f"Document with name '{name}' already exists in departments: {failure_departments}."
            response_data = {
                "message": failure_message,
            }
            return Response(response_data, status=status.HTTP_409_CONFLICT)

        success_message = f"Document '{name}' added to departments successfully."
        response_data = {
            "message": success_message,
            "created_documents": created_documents
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

        
from rest_framework import serializers
from rest_framework.filters import SearchFilter, OrderingFilter 
import logging
from django.db.models import OuterRef, Exists, Count, Case, When, Value, IntegerField
from documents.models import DocumentKeyPoints , DocumentSummary, DocumentQuiz

logger = logging.getLogger(__name__)



class DepartmentsDocumentsListAPIView(generics.ListAPIView):
    serializer_class = DepartmentsDocumentsSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['id', 'name', 'file', 'department__name', 'published', 'created_at', 'updated_at', 'added_by__first_name']
    ordering_fields = ['id', 'name', 'file', 'department__name', 'published', 'created_at', 'updated_at', 'added_by__first_name']
    ordering = ['id', 'name', 'file', 'department__name', 'published', 'created_at', 'updated_at', 'added_by__first_name']
    queryset = DepartmentsDocuments.objects.filter(is_active=True)

    def get_queryset(self):
        user = self.request.user
        department_id = self.request.query_params.get('department_id', None)
        user_id = self.request.query_params.get('user_id', None)

        if user.role in ["Super Admin", "Admin"]:
            queryset = DepartmentsDocuments.objects.filter(is_active=True)
            if department_id:
                queryset = queryset.filter(department__id=department_id)

            if user.role == "Admin":
                try:
                    admin_company = AdminUser.objects.get(admin=user, is_active=True).company
                    queryset = queryset.filter(department__company=admin_company)
                except AdminUser.DoesNotExist:
                    raise serializers.ValidationError({"Unauthorized": "You are blocked or deleted"})

            # Annotate the queryset with is_summary and is_keypoints
            queryset = queryset.annotate(
                is_summary=Exists(DocumentSummary.objects.filter(document=OuterRef('id'))),
                is_keypoints=Exists(DocumentKeyPoints.objects.filter(document=OuterRef('id'))),
                is_quizzes=Exists(DocumentQuiz.objects.filter(document=OuterRef('id'), upload=True)),
                quizzes= Case(
                    When(
                        Exists(DocumentQuiz.objects.filter(document=OuterRef('id'), upload=True)),
                        then=Count('documentquiz', filter=Exists(DocumentQuiz.objects.filter(document=OuterRef('id'), upload=True))),
                    ),
                    default=Value(0),
                    output_field=IntegerField()
                )
            )
            
            return queryset

        if user.role == "User":
            try:
                if user_id:
                    user_teams = CompaniesTeam.objects.filter(id=user_id, is_active=True)
                else:
                    user_teams = CompaniesTeam.objects.filter(members=user, is_active=True)

                queryset = DepartmentsDocuments.objects.filter(
                    assigned_users__in=user_teams, is_active=True
                )
                
                if department_id:
                    queryset = queryset.filter(department__id=department_id)

                queryset = queryset.distinct().annotate(
                    is_summary=Exists(DocumentSummary.objects.filter(document=OuterRef('id'))),
                    is_keypoints=Exists(DocumentKeyPoints.objects.filter(document=OuterRef('id'))),
                    is_quizzes=Exists(DocumentQuiz.objects.filter(document=OuterRef('id'), upload=True)),
                    quizzes= Case(
                        When(
                            Exists(DocumentQuiz.objects.filter(document=OuterRef('id'), upload=True)),
                            then=Count('documentquiz', filter=Exists(DocumentQuiz.objects.filter(document=OuterRef('id'), upload=True))),
                        ),
                        default=Value(0),
                        output_field=IntegerField()
                    )

                )    
                
                return queryset
            except CompaniesTeam.DoesNotExist:
                raise serializers.ValidationError({"Unauthorized": "The specified team does not exist or you are blocked"})

        raise serializers.ValidationError({"Unauthorized": "You are not authorized to view these documents."}, code="unauthorized")

    
from .serializers import DepartmentsDocumentsUpdateSerializer
class DepartmentsDocumentsUpdateDestroyRetrieveAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DepartmentsDocuments.objects.filter(is_active=True)
    serializer_class = DepartmentsDocumentsUpdateSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        if request.user.role == "User":
            raise serializers.ValidationError({"Access Denied": "You do not have permission to update documents."})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document_id = kwargs["id"]
        is_summary = DocumentSummary.objects.filter(document=document_id).exists(),
        is_keypoints = DocumentKeyPoints.objects.filter(document=document_id).exists(),
        is_quizzes = DocumentQuiz.objects.filter(document=document_id, upload=True).count()
        quizzes = 0
        if is_quizzes:
            quizzes = is_quizzes
        update_response = self.update(request, *args, **kwargs)
        if update_response.status_code == status.HTTP_200_OK:
            updated_data = update_response.data
            combined_data = {
                **updated_data,
                'is_summary': is_summary[0],
                'is_keypoints': is_keypoints[0],
                'is_quizzes': is_quizzes, 
                'quizzes': quizzes
            }

            return Response(combined_data, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        if request.user.role == "User":
            raise serializers.ValidationError({"Access Denied": "You do not have permission to delete documents."})
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({"Delete Status": "Successfully Removed the Document", "id": instance.id}, status=status.HTTP_202_ACCEPTED)
class AssignDocumentsToUsersAPIView(APIView):
    def post(self, request, document_id):
        try:
            document = DepartmentsDocuments.objects.get(id=document_id)
        except DepartmentsDocuments.DoesNotExist:
            return Response({"message": "Document not found."}, status=status.HTTP_404_NOT_FOUND)
        
        users = request.data.get('users', [])
        for user_id in users:
            try:
                user = CompaniesTeam.objects.get(id=user_id)
                document.users.add(user)
            except CompaniesTeam.DoesNotExist:
                return Response({"message": "Users not found."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"message": "Document assigned to users successfully."}, status=status.HTTP_200_OK)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from departments.models import DepartmentsDocuments
from documents.models import DocumentQuiz, QuizQuestions
