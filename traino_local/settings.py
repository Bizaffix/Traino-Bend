"""
Django settings for traino_local project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
# traino_local/settings.py
from __future__ import absolute_import, unicode_literals
from pathlib import Path
import os
from datetime import timedelta



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-l9e&n!faln0p-p1es_bs3aqi$7kguo79_yaag5x5tke$9#c!78'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    # '127.0.0.1:3000',
    "*",
    'http://f84gwgcgcskww8k8g0o4c4wc.145.223.101.115.sslip.io', #remove below 3 lines
    'http://127.0.0.1:8000',
    'http://145.223.101.115:8000',
    '145.223.101.115',
    '145.223.101.115:8000',
    '127.0.0.1:8000',
    'localhost:3000',
    '127.0.0.1',
    'https://f84gwgcgcskww8k8g0o4c4wc.145.223.101.115.sslip.io'
    'f84gwgcgcskww8k8g0o4c4wc.145.223.101.115.sslip.io/',
    'localhost',
    'app.traino.ai',
    'traino-ai-api.vercel.app',
    'dashboard.traino.ai',
    'http://f84gwgcgcskww8k8g0o4c4wc.145.223.101.115.sslip.io',
    "trainoaitest1.vercel.app",  # Add this
]


AUTH_USER_MODEL = 'accounts.CustomUser'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    #  'post_office',
    'documents',
    'dal',
    'dal_select2',
    'teams',
    'rest_framework',
    'djoser',
    'corsheaders',
    'django_filters',
    'company',
    'api',
    'departments',
    'emailfunc',
    'reminderemailfunc',
    'django_cron',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'traino_local.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates/')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'traino_local.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db/db.sqlite3',
    }
}



# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATIC_DIR = {
    os.path.join(BASE_DIR, 'public/static/')
}

# MEDIA_ROOT = os.path.join(BASE_DIR, 'public/static/')
MEDIA_ROOT = os.path.join(BASE_DIR, '')
MEDIA_URL = '/'


# AWS email configurations

# AWS_ACCESS_KEY_ID = 'AKIAVIMMZLH3BTHFTKMK'
# AWS_SECRET_ACCESS_KEY = 'BDsJw26hIA6Bm6QBX7xk+vQdAc1ZODMOYtpADd4HDUKv'


# EMAIL_BACKEND = 'django_ses.SESBackend'

# AWS_SES_REGION_NAME = 'us-east-1'
# AWS_SES_REGION_ENDPOINT = 'email-smtp.us-east-1.amazonaws.com'



# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# JWT Configurations

REST_FRAMEWORK = {
    'DATETIME_FORMAT': "%m/%d/%Y %H:%M:%S",
    'DEFAULT_PAGINATION_CLASS':'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE':10,
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}


CORS_ALLOWED_ORIGINS = [
    
    "https://dashboard.traino.ai",
    # "https://dashboard.traino.ai/media/documents/",
    "https://app.traino.ai",
    # "https://app.traino.ai/media/documents/",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    # "https://localhost:3000/media/documents/",
    "http://127.0.0.1:3000",
    "https://traino-ai-api.vercel.app",
    "https://trainoaitest1.vercel.app",  
    # "https://traino-ai-api.vercel.app/media/documents/",
]


CORS_ALLOW_ALL_ORIGINS = True


CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]

CSRF_TRUSTED_ORIGINS = [
    "https://app.traino.ai",
    # "https://app.traino.ai/media/documents/",
    "https://traino-ai-api.vercel.app",
    # "https://traino-ai-api.vercel.app/media/documents/",
    "https://dashboard.traino.ai",
    # "https://dashboard.traino.ai/media/documents/",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8000"
    # "https://localhost:3000/media/documents/",
    "http://127.0.0.1:3000",
    "https://trainoaitest1.vercel.app",  # Add this line
]

# Email Configurations
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "mail.privateemail.com" #nsm TODO: Remove/Replace it
# EMAIL_PORT = 465
# EMAIL_HOST_USER = 'no-reply@traino.ai' #os.environ.get('EMAIL_USER')
# EMAIL_HOST_PASSWORD = 'hello123!@' #os.environ.get('EMAIL_PASS')
# EMAIL_DEFAULT_FROM = 'no-reply@traino.ai' # os.environ.get('EMAIL_USER')  # your sender email addreass
# EMAIL_USE_TLS = False
# EMAIL_USE_SSL = True
# DEFAULT_FROM_EMAIL = 'no-reply@traino.ai'

#nsm
# Set your AWS SES SMTP credentials
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'  # Replace {region} with your AWS SES region
EMAIL_PORT = 587  # 25, 587 or 2587
EMAIL_HOST_USER = 'AKIAVIMMZLH3BTHFTKMK'  # SES SMTP username
EMAIL_HOST_PASSWORD = 'BDsJw26hIA6Bm6QBX7xk+vQdAc1ZODMOYtpADd4HDUKv'  # SES SMTP password
DEFAULT_FROM_EMAIL = 'no-reply@traino.ai'

# SeS Emails Configurations
# traino_local/settings.py

# EMAIL_BACKEND = 'django_ses.SESBackend'
# AWS_SES_REGION_NAME = 'us-east-1'
# AWS_SES_REGION_ENDPOINT = 'email-smtp.us-east-1.amazonaws.com'
# AWS_ACCESS_KEY_ID = 'AKIAVIMMZLH3BTHFTKMK'
# AWS_SECRET_ACCESS_KEY = 'BDsJw26hIA6Bm6QBX7xk+vQdAc1ZODMOYtpADd4HDUKv'
# EMAIL_HOST = "email-smtp.us-east-1.amazonaws.com"
# EMAIL_PORT = 467
# EMAIL_HOST_USER = 'no-reply@traino.ai'
# EMAIL_HOST_PASSWORD = 'hello123!@'
# EMAIL_USE_TLS = True
# EMAIL_USE_SSL = True
# DEFAULT_FROM_EMAIL = 'no-reply@traino.ai'


# DJOSER Settings

DJOSER = {
    'LOGIN_FIELD': 'email',
    'PASSWORD_RESET_CONFIRM_URL': '/password/reset/confirm/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': False,
    'SEND_CONFIRMATION_EMAIL': False,
    'PASSWORD_CHANGED_EMAIL_CONFIRMATION': False,
    'ACTIVATION_URL': '/activate/{uid}/{token}',
    'USER_CREATE_PASSWORD_RETYPE': True, #
    'SET_PASSWORD_RETYPE': True,
    'PASSWORD_RESET_CONFIRM_RETYPE': False, #
    'LOGOUT_ON_PASSWORD_CHANGE': True, #
    'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': False,
    'TOKEN_MODEL': None, # To delete user must set it to None
    'SERIALIZERS': {
        'user_create': 'api.serializers.UserCreateSerializer',
        'user': 'api.serializers.UserCreateSerializer',
        'user_delete': 'djoser.serializers.UserDeleteSerializer',
    },
    'EMAIL': {
        'activation': 'api.email.ActivationEmail',
        'confirmation': 'api.email.ConfirmationEmail',
        'password_reset': 'api.email.PasswordResetEmail',
        'password_changed_confirmation': 'api.email.PasswordChangedConfirmationEmail',
    },
}


CELERY_BROKER_URL = 'redis://localhost:6379/0'  # or your broker URL
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # or your result backend URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

Q_CLUSTER = {
    'name': 'traino_cluster',
    'workers': 4,
    'timeout': 60,
    'django_redis': 'redis://localhost:6379/0',  # You can also use Django database-backed setup
    'save': True,
    'catch_up': False,  # Prevents tasks from running until they're scheduled
}
# Simple JWT Settings

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}

# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# uwsgi --socket /var/www/app.traino.ai/app.traino.ai.sock --module /var/www/app.traino.ai/traino_local.wsgi --chmod-socket=666 --uid www-data --gid www-data --master
# uwsgi --emperor /var/www/app.traino.ai/vassals --uid www-data --gid www-data

# uwsgi --socket ./app.traino.ai.sock --module ./traino_local.wsgi --chmod-socket=666 --uid www-data --gid www-data --master
# uwsgi --socket /var/www/app.traino.ai/traino_sock/app.traino.ai.sock --module /var/www/app.traino.ai/traino_local.wsgi --chmod-socket=666 --uid www-data --gid www-data --master --thunder-lock

# sudo uwsgi --socket traino_sock/app.traino.ai.sock --module traino_local.wsgi --chmod-socket=666 --uid www-data --gid www-data --master --thunder-lock --enable-threads

# pgrep gunicorn
# kill -TERM <PID>
# gunicorn -c conf/gunicorn_config.py traino_local.wsgi &
