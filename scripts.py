import smtplib
from email.mime.text import MIMEText
from post_office import mail

smtp_server = 'email-smtp.us-east-1.amazonaws.com'
smtp_port = 465
smtp_user =  'AKIAVIMMZLH3BTHFTKMK'
smtp_password = 'BDsJw26hIA6Bm6QBX7xk+vQdAc1ZODMOYtpADd4HDUKv'
from_email = 'no-reply@traino.ai'
to_email = 'mshariq28022000@gmail.com'
subject = 'Test Email'
body = 'This is a test email. From Muhammad Shariq Shafiq'

POST_OFFICE = {
    'BACKENDS': {
        'default': 'django_ses.SESBackend',
    },
    'DEFAULT_PRIORITY': 'now',
}

msg = MIMEText(body)
msg['Subject'] = subject
msg['From'] = from_email
msg['To'] = to_email


try:
    mail.send(
    recipients=to_email, # List of email addresses also accepted
    sender= from_email,
    subject='My email',
    message='Hi there!',
    html_message='Hi <strong>there</strong>!',
)
    print('Email sent successfully!')
except Exception as e:
    print(f'Failed to send email: {e}')

# try:
#     server = smtplib.SMTP_SSL(smtp_server, smtp_port)
#     server.login(smtp_user, smtp_password)
#     server.mail(from_email, [to_email], msg.as_string())
#     server.quit()
#     print('Email sent successfully!')
# except Exception as e:
#     print(f'Failed to send email: {e}')
