SECRET_KEY = 'jdjlajdke'
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'post_office',
]
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_SES_ACCESS_KEY_ID = 'AKIAVIMMZLH3BTHFTKMK'
AWS_SES_SECRET_ACCESS_KEY = 'BDsJw26hIA6Bm6QBX7xk+vQdAc1ZODMOYtpADd4HDUKv'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':'db/db.sqlite3',
    }
}