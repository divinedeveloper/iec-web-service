"""Production settings and globals."""
from .base import *
import logging

########## SITE CONFIGURATION
ALLOWED_HOSTS = ['139.59.31.145', 'localhost', '127.0.0.1']
########## END SITE CONFIGURATION

########## DATABASE CONFIGURATION
# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

_MONGODB_USER = 'prod_iec_admin'
_MONGODB_PASSWD = 'prod_iecpass'
_MONGODB_HOST = '127.0.0.1'
_MONGODB_PORT = '27017'
_MONGODB_NAME = 'prod_iec'
_MONGODB_DATABASE_HOST = \
    'mongodb://%s:%s@%s:%s/%s' \
    % (_MONGODB_USER, _MONGODB_PASSWD, _MONGODB_HOST, _MONGODB_PORT, _MONGODB_NAME)

try:
	mongoengine.connect(_MONGODB_NAME, host= _MONGODB_DATABASE_HOST)
except Exception as e:
	logging.debug( '%s (%s)' % (e.args, type(e)))

########## END DATABASE CONFIGURATION
