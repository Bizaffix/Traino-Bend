import os
import django
from django.conf import settings

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traino_local.settings')
django.setup()

from post_office import mail

from_email = 'no-reply@traino.ai'
to_email = 'mshariq28022000@gmail.com'
subject = 'Test Email'
body = 'This is a test email. From Muhammad Shariq Shafiq'

try:
    mail.send(
        recipients=[to_email],  # List of email addresses also accepted
        sender=from_email,
        subject=subject,
        message=body,
        html_message='This is a <strong>test email</strong>. From Muhammad Shariq Shafiq',
    )
    print('Email sent successfully!')
except Exception as e:
    print(f'Failed to send email: {e}')
