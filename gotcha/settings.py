"""
Django settings for gotcha project.

Generated by 'django-admin startproject' using Django 3.0.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import django_heroku
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
if os.environ.get('DEBUG'):
    DEBUG = True

ALLOWED_HOSTS = ['http://127.0.0.1:8000/', "*"]


# Application definition

INSTALLED_APPS = [
    'accounts',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'ckeditor',
    'tempus_dominus',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gotcha.urls'

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

WSGI_APPLICATION = 'gotcha.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = os.environ.get('TIME_ZONE')

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

EMAIL_BACKEND="sendgrid_backend.SendgridBackend"
if os.environ.get('DEBUG'):
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]

# DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")

AUTH_PASSWORD_VALIDATORS = []

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': [["Bold", "Italic", "Underline", "Strike"],
                        ['NumberedList', 'BulletedList', "Indent", "Outdent", 'JustifyLeft', 'JustifyCenter',
                        'JustifyRight', 'JustifyBlock'],
                        ["Table", "Link", "Unlink", "Anchor", "SectionLink", "Subscript", "Superscript"], ['Undo', 'Redo'], ["Source"],
                        ["Maximize"]],
        'width': 'auto',
        'height': 'auto',
        'extraPlugins': ','.join(
            [
               'autocorrect',
            ]
        ),
    },
}

# Celery settings
# CELERY_BROKER_URL = 'pyamqp://guest@localhost//'
# CELERY_BROKER_URL = "amqp://czlylfvc:OpVgWdDlLhll2skdsqapF0c8AWZr5eOs@fox.rmq.cloudamqp.com/czlylfvc"
# CELERY_BROKER_URL = os.environ['CLOUDAMQP_URL']
CELERY_BROKER_URL = "pyamqp://dyfobtkj:YsAQDCL9MtX8dNjL7a91-fdlhJzaR9H2@vulture.rmq.cloudamqp.com/dyfobtkj" # self-made
# CELERY_BROKER_URL = "redis://rediscloud:HwvYf4EUPwSi6WmGEiC49K28ZCymmUSp@redis-18821.c90.us-east-1-3.ec2.cloud.redislabs.com:18821"
# CELERY_BROKER_POOL_LIMIT = 3
# CELERY_WORKER_CONCURRENCY = 1
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TASK_ALWAYS_EAGER = True
# CELERY_BROKER_URL=os.environ['REDIS_URL']
# CELERY_BROKER_URL="redis://127.0.0.1/"
# CELERY_ACCEPT_CONTENT = ['application/json']
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_BACKEND=os.environ['REDIS_URL']
# CELERY_RESULT_BACKEND="amqp://dyfobtkj:YsAQDCL9MtX8dNjL7a91-fdlhJzaR9H2@vulture.rmq.cloudamqp.com/dyfobtkj"

TEMPUS_DOMINUS_LOCALIZE = True

django_heroku.settings(locals())
