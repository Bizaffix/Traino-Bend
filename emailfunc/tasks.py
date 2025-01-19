# from celery import shared_task
# from django.core.mail import EmailMessage

# @shared_task
# def send_scheduled_email(subject, html_content, from_email, recipient_list):
#     """
#     Task to send emails asynchronously with the given details.
#     """
#     email_message = EmailMessage(
#         subject=subject,
#         body=html_content,
#         from_email=from_email,
#         to=recipient_list
#     )
#     email_message.content_subtype = "html"  # Specify content type as HTML
#     email_message.send()

# yourapp/tasks.py
from celery import shared_task
from django.core.mail import EmailMessage

@shared_task
def send_email_task(subject, message, from_email, recipient_list):
    try:
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.send()
        return "Email sent successfully"
    except Exception as e:
        return str(e)
