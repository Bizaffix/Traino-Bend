import smtplib
from email.mime.text import MIMEText

smtp_server = 'mail.privateemail.com'
smtp_port = 465
smtp_user =  'no-reply@traino.ai'
smtp_password = 'hello123!@'
from_email = 'no-reply@traino.ai'
to_email = 'mshariq28022000@hotmail.com'
subject = 'Test Email'
body = 'This is a test email. From Muhammad Shariq Shafiq'

msg = MIMEText(body)
msg['Subject'] = subject
msg['From'] = from_email
msg['To'] = to_email

try:
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.login(smtp_user, smtp_password)
    server.sendmail(from_email, [to_email], msg.as_string())
    server.quit()
    print('Email sent successfully!')
except Exception as e:
    print(f'Failed to send email: {e}')
