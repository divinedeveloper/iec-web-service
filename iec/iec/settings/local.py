"""Local settings and globals."""
from .base import *

########## DEBUG CONFIGURATION
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


########## END DEBUG CONFIGURATION

########## DATABASE CONFIGURATION
# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

_MONGODB_USER = 'iecadmin'
_MONGODB_PASSWD = 'iecpass'
_MONGODB_HOST = '127.0.0.1'
_MONGODB_PORT = '27017'
_MONGODB_NAME = 'iec'
_MONGODB_DATABASE_HOST = \
    'mongodb://%s:%s@%s:%s/%s' \
    % (_MONGODB_USER, _MONGODB_PASSWD, _MONGODB_HOST, _MONGODB_PORT, _MONGODB_NAME)

try:
	mongoengine.connect(_MONGODB_NAME, host= _MONGODB_DATABASE_HOST)
except Exception as e:
    print '%s (%s)' % (e.message, type(e))

########## END DATABASE CONFIGURATION