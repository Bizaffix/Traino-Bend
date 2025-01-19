from django.shortcuts import render
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.views import View
import json
from django.template.loader import render_to_string

class SendEmailAPI(View):
    def post(self, request, *args, **kwargs):
        # Initialize email tracking lists
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
            from_email = "no-reply@traino.ai"
            recipient_list = [email]

            # Render the HTML template with dynamic data
            html_content = render_to_string(
                'emails/Key_notification.html',
                {'to_name': name, 'to_email': email}
            )

            # Create the email object
            email_message = EmailMessage(
                subject=subject,
                body=html_content,
                from_email=from_email,
                to=recipient_list
            )
            email_message.content_subtype = "html"  # Mark the content as HTML

            try:
                email_message.send()
                success_emails.append(email)
            except Exception as e:
                failed_emails.append({"email": email, "error": str(e)})

        return JsonResponse({
            "status": "completed",
            "success": success_emails,
            "failed": failed_emails
        })
