"""
Django settings for iec project.

Generated by 'django-admin startproject' using Django 1.8.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import mongoengine

########## PATH CONFIGURATION
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
########## END PATH CONFIGURATION



########## SECRET CONFIGURATION
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = os.environ['A_SECRET_KEY']
# Read later from a non versioned file

SECRET_KEY = 'fip!($r&3_@n5%*ldqcwggk++^cdto209l$pv_mnuzzsow0)@1'
########## END SECRET CONFIGURATION


########## DEBUG CONFIGURATION
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
########## END DEBUG CONFIGURATION


########## SITE CONFIGURATION
ALLOWED_HOSTS = []
########## END SITE CONFIGURATION


########## APP CONFIGURATION
# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_mongoengine',

    'iec',
    'iec_lookup',
)
########## END APP CONFIGURATION

########## MIDDLEWARE CONFIGURATION
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)
########## END MIDDLEWARE CONFIGURATION


########## URL CONFIGURATION
ROOT_URLCONF = 'iec.urls'
########## END URL CONFIGURATION

########## TEMPLATE CONFIGURATION
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, BASE_DIR+'/templates')],
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
########## END TEMPLATE CONFIGURATION

########## WSGI CONFIGURATION
WSGI_APPLICATION = 'iec.wsgi.application'
########## END WSGI CONFIGURATION


########## DATABASE CONFIGURATION

#NoSQL DB configuration can be found in respective environment files

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

########## END DATABASE CONFIGURATION

########## GENERAL CONFIGURATION
# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
########## END GENERAL CONFIGURATION


########## STATIC FILE CONFIGURATION
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
STATIC_URL = '/static/'
########## END STATIC FILE CONFIGURATION


########## REST FRAMEWORK CONFIGURATION
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
    ],
    'EXCEPTION_HANDLER': 'iec.iec_lookup.custom_exceptions.iec_custom_exception_handler',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}
########## END REST FRAMEWORK CONFIGURATION

########## GLOBAL STRING VALUES CONFIGURATION

DGFT_SITE_URL = "http://dgft.delhi.nic.in:8100/dgft/IecPrint"
DGFT_IEC_NOT_PROPER_ERROR = "IEC is not proper"
DGFT_APPLICANT_NAME_NOT_PROPER_ERROR = "Applicant name is not proper"
DGFT_SUCCESS_REPLY = "Importer Exporter Code"
DGFT_PARTY_NAME_ADDRESS_STRING = "Party Name and Address" 
DGFT_BANKER_DETAIL_STRING = "Banker Detail"
IEC_STATUS_STRING = "IEC Status"

# DGFT_SUCCESS_RESPONSE = """ """

########## END GLOBAL STRING VALUES CONFIGURATION




