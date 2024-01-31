from django.shortcuts import render
from django.http import JsonResponse
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.document_loaders import PyPDFLoader
from .models import UserDocuments, QuizQuestions, DocumentQuiz
from PyPDF2 import PdfReader
from langchain.prompts import PromptTemplate
import os
import json
from django.shortcuts import redirect
from django.template.loader import render_to_string

openai_api_key = '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'
os.environ['OPENAI_API_KEY'] = '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'

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

            document = UserDocuments.objects.get(id=document_id)
            if document.file.path is not None:
                print("test: 1")
                # Instantiate the LLM model
                #llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
                llm = ChatOpenAI(model_name='gpt-3.5-turbo')
                print("test: 2")
                print(document.file.path)

                loader = PyPDFLoader(document.file.path)
                #docs = loader.load_and_split()
                
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

            document = UserDocuments.objects.get(id=document_id)
            if document.file.path is not None:
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
                data['document_keypoints'] = chain.run(text)
                #print(len(data['document_keypoints']))
                #print(data['document_keypoints'])
                #print("test: 6")
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

            document = UserDocuments.objects.get(id=document_id)
            if document.file.path is not None:
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
    return JsonResponse(data, status=200)