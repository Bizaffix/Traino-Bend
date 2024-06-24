import os
from django.core.mail import send_mail
import django
from django.conf import settings

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traino_local.settings')
django.setup()

subject = 'hello'
from_email = 'no-reply@traino.ai'
to_email = ["mshariq28022000@hotmail.com"]
message = "Test mail"

try:
    send_mail(subject, message, from_email, to_email, fail_silently=False)
    print("Successfully Sent")
except Exception as e:
    print(f'Something went wrong: {e}')
