from django.shortcuts import render

# Create your views here.
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views import View
import json

class SendEmailAPI(View):
    def post(self, request, *args, **kwargs):
        success_emails = []
        failed_emails = []

        # Get the data from the request body
        try:
            request_data = json.loads(request.body)
            data = request_data.get('emails', [])
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        for email, name in data:
            subject = f"Hello, {name}!"
            message = f"Dear {name},\n\nThis is a test email sent via Django.\n\nBest regards,\nYour Team"
            from_email = "no-reply@traino.ai"
            recipient_list = [email]

            try:
                send_mail(subject, message, from_email, recipient_list)
                success_emails.append(email)
            except Exception as e:
                failed_emails.append({"email": email, "error": str(e)})

        return JsonResponse({
            "status": "completed",
            "success": success_emails,
            "failed": failed_emails
        })
