# from django.shortcuts import render
# from django.core.mail import EmailMessage
# from django.http import JsonResponse
# from django.views import View
# import json
# from django.template.loader import render_to_string

# class SendEmailAPI(View):
#     def post(self, request, *args, **kwargs):
#         # Initialize email tracking lists
#         success_emails = []
#         failed_emails = []

#         # Get the data from the request body
#         try:
#             request_data = json.loads(request.body)
#             data = request_data.get('emails', [])
#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Invalid JSON format"}, status=400)

#         for email, name in data:
#             subject = f"Hello, {name}!"
#             from_email = "no-reply@traino.ai"
#             recipient_list = [email]

#             # Render the HTML template with dynamic data
#             html_content = render_to_string(
#                 'emails/quiz_notification.html',
#                 {'to_name': name, 'to_email': email}
#             )

#             # Create the email object
#             email_message = EmailMessage(
#                 subject=subject,
#                 body=html_content,
#                 from_email=from_email,
#                 to=recipient_list
#             )
#             email_message.content_subtype = "html"  # Mark the content as HTML

#             try:
#                 email_message.send()
#                 success_emails.append(email)
#             except Exception as e:
#                 failed_emails.append({"email": email, "error": str(e)})

#         return JsonResponse({
#             "status": "completed",
#             "success": success_emails,
#             "failed": failed_emails
#         })


# import json
# from django.utils.timezone import now
# from django.template.loader import render_to_string
# from django.http import JsonResponse
# from django.views import View
# from datetime import timedelta
# from .tasks import send_scheduled_email

# class SendEmailAPI(View):
#     def post(self, request, *args, **kwargs):
#         try:
#             # Parse the incoming JSON request
#             request_data = json.loads(request.body)
#             data = request_data.get('emails', [])
#             schedule_days = request_data.get('schedule_days', 1)  # Default to 3 days

#             # Validate schedule_days
#             if schedule_days not in [1, 3, 5, 7]:
#                 return JsonResponse({"error": "Invalid schedule_days. Choose from 1, 3, 5, or 7."}, status=400)

#             # Process emails
#             success_emails = []
#             failed_emails = []

#             for email, name in data:
#                 subject = f"Hello, {name}!"
#                 from_email = "no-reply@traino.ai"
#                 recipient_list = [email]

#                 # Render HTML content
#                 html_content = render_to_string(
#                     'emails/quiz_notification.html',
#                     {'to_name': name, 'to_email': email}
#                 )

#                 # Schedule the email
#                 try:
#                     schedule_time = now() + timedelta(days=schedule_days)
#                     send_scheduled_email.apply_async(
#                         args=[subject, html_content, from_email, recipient_list],
#                         eta=schedule_time  # Schedule the task
#                     )
#                     success_emails.append(email)
#                 except Exception as e:
#                     failed_emails.append({"email": email, "error": str(e)})

#             return JsonResponse({
#                 "status": "completed",
#                 "success": success_emails,
#                 "failed": failed_emails
#             })

#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Invalid JSON format"}, status=400)



from django.shortcuts import render
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.views import View
import json
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta

class SendEmailAPI(View):
    def post(self, request, *args, **kwargs):
        # Initialize email tracking lists
        success_emails = []
        failed_emails = []

        # Get the data from the request body
        try:
            request_data = json.loads(request.body)
            emails_data = request_data.get('emails', [])
            schedule_type = request_data.get('schedule', 'daily')  # Default to daily if not provided
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        # Determine the time for sending based on the schedule
        current_time = timezone.now()
        should_send_email = False

        # Logic for different schedules
        if schedule_type == 'daily':
            should_send_email = True  # Send daily
        elif schedule_type == 'weekly':
            # Check if it's the correct day for sending (e.g., Monday)
            if current_time.weekday() == 0:  # Monday (0=Monday, 1=Tuesday, ...)
                should_send_email = True
        elif schedule_type == 'monthly':
            # Check if it's the first day of the month
            if current_time.day == 1:
                should_send_email = True
        elif schedule_type == 'thrice_a_week':
            # Check if it's a specified day for thrice-weekly (e.g., Monday, Wednesday, Friday)
            if current_time.weekday() in [0, 2, 4]:  # 0=Monday, 2=Wednesday, 4=Friday
                should_send_email = True

        if should_send_email:
            for email, name in emails_data:
                subject = f"Hello, {name}!"
                from_email = "no-reply@traino.ai"
                recipient_list = [email]

                # Render the HTML template with dynamic data
                html_content = render_to_string(
                    'emails/quiz_notification.html',
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
        else:
            return JsonResponse({
                "status": "skipped",
                "message": f"Emails not sent as it's not the correct time for the {schedule_type} schedule."
            })
