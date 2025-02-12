from django.shortcuts import render
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.views import View
import json
from django.template.loader import render_to_string
from departments.models import DepartmentsDocuments
from rest_framework import status

from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from django.conf import settings
import base64


from documents.models import (
    DocumentSummary,
    DocumentKeyPoints,
)


class SendEmailAPI(APIView):
    def post(self, request, *args, **kwargs):

        def image_to_base64(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode("utf-8")

        # base64_image =
        # Initialize email tracking lists
        success_emails = []
        failed_emails = []

        # Get the data from the request body
        try:
            request_data = json.loads(request.body)
            document_id = request_data.get("document_id")
            date = request_data.get("date")
            doc_name = request_data.get("doc_name")  # Extract document ID
            data = request_data.get("emails", [])
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        # Validate and fetch the document
        if not document_id:
            return JsonResponse({"error": "document_id is required"}, status=400)
        try:
            document = DepartmentsDocuments.objects.get(id=document_id, is_active=True)
        except DepartmentsDocuments.DoesNotExist:
            return JsonResponse({"error": "No Document Found"}, status=404)

        # Fetch key points (quiz questions) from the document
        try:
            keypoints = DocumentKeyPoints.objects.filter(document=document).first()
            if keypoints is None:
                return Response(
                    {"error": "No keypoints found for this document"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        except DocumentSummary.DoesNotExist:
            return Response(
                {"error": "No keypoints found for this document"},
                status=status.HTTP_404_NOT_FOUND,
            )

        key_points = keypoints.keypoints.split("\n")  # Split the key points

        # Process each email
        for email, name in data:
            subject = f"Hello, {name}!"
            from_email = "no-reply@traino.ai"
            recipient_list = [email]

            # Render the HTML template with dynamic data
            html_content = render_to_string(
                "emails/email_template.html",
                {
                    "to_name": name,
                    "to_email": email,
                    "key_points": key_points[:3],  # Pass the dynamic key points
                    "doc_name": doc_name,
                    "date": date,
                    "base_url": settings.BASE_URL,
                    "fb": image_to_base64("templates/fb.png"),
                    "in": image_to_base64("templates/in.png"),
                    "insta": image_to_base64("templates/insta.png"),
                    "x": image_to_base64("templates/x.png"),
                    "footer_logo": image_to_base64("templates/footer_logo.png"),
                    "header_title": image_to_base64("templates/header_title.png"),
                    "header": image_to_base64("templates/header.png"),
                },
            )

            # Create the email object
            email_message = EmailMessage(
                subject=subject,
                body=html_content,
                from_email=from_email,
                to=recipient_list,
            )
            email_message.content_subtype = "html"  # Mark the content as HTML

            try:
                email_message.send()
                success_emails.append(email)
            except Exception as e:
                failed_emails.append({"email": email, "error": str(e)})

        return Response(
            {"status": "completed", "success": success_emails, "failed": failed_emails},
            status=status.HTTP_200_OK,
        )


# from django.shortcuts import render
# from django.core.mail import EmailMessage
# from django.http import JsonResponse
# from django.views import View
# from django.template.loader import render_to_string
# import json
# import logging

# logger = logging.getLogger(__name__)

# class SendEmailAPI(View):
#     def post(self, request, *args, **kwargs):
#         success_emails = []
#         failed_emails = []

#         try:
#             request_data = json.loads(request.body)
#             document_id = request_data.get('document_id')
#             data = request_data.get('emails', [])
#             logger.info(f"Request received with document_id: {document_id} and emails: {data}")
#         except json.JSONDecodeError:
#             logger.error("Invalid JSON format in request body")
#             return JsonResponse({"error": "Invalid JSON format"}, status=400)

#         if not document_id:
#             logger.error("document_id is missing in the request")
#             return JsonResponse({"error": "document_id is required"}, status=400)

#         try:
#             document = DepartmentsDocuments.objects.get(id=document_id, is_active=True)
#             logger.info(f"Document retrieved: {document}")
#         except DepartmentsDocuments.DoesNotExist:
#             logger.error(f"No document found with id {document_id}")
#             return JsonResponse({"error": "No Document Found"}, status=404)

#         try:
#             quizzes = DocumentQuiz.objects.filter(document=document, upload=True)
#             key_points = [quiz.name for quiz in quizzes]
#             logger.info(f"Key points extracted: {key_points}")
#         except Exception as e:
#             logger.error(f"Failed to fetch quizzes: {str(e)}")
#             return JsonResponse({"error": f"Failed to fetch quizzes: {str(e)}"}, status=500)

#         if not key_points:
#             logger.warning("No quizzes found for the document")
#             return JsonResponse({"error": "No quizzes available for this document"}, status=404)

#         for email, name in data:
#             try:
#                 html_content = render_to_string(
#                     'emails/Key_notification.html',
#                     {'to_name': name, 'to_email': email, 'key_points': key_points}
#                 )
#                 email_message = EmailMessage(
#                     subject=f"Hello, {name}!",
#                     body=html_content,
#                     from_email="no-reply@traino.ai",
#                     to=[email]
#                 )
#                 email_message.content_subtype = "html"
#                 email_message.send()
#                 success_emails.append(email)
#                 logger.info(f"Email sent successfully to {email}")
#             except Exception as e:
#                 logger.error(f"Failed to send email to {email}: {str(e)}")
#                 failed_emails.append({"email": email, "error": str(e)})

#         return JsonResponse({"status": "completed", "success": success_emails, "failed": failed_emails})
