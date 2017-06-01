from .base import *
import mongoengine
import logging

########## DEBUG CONFIGURATION
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
########## END DEBUG CONFIGURATION

########## FULL URL CONFIGURATION FOR UNIT & INTEGRATION TESTS
IEC_LOOKUP_URL = 'http://127.0.0.1:8000/iec/api/v1/lookup/'
IEC_RETRIEVE_URL = 'http://127.0.0.1:8000/iec/api/v1/retrieve/'

IEC_LOOKUP_MINI_URL = '/lookup/'
IEC_RETRIEVE_MINI_URL = '/retrieve/'
########## END FULL URL CONFIGURATION FOR INTEGRATION TESTS



########## DATABASE CONFIGURATION
# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

mongoengine.connection.disconnect() # disconnect main db first

_MONGODB_USER = 'iectestadmin'
_MONGODB_PASSWD = 'iectestpass'
_MONGODB_HOST = '127.0.0.1'
_MONGODB_PORT = '27017'
_MONGODB_NAME = 'test_iec'
_MONGODB_DATABASE_HOST = \
    'mongodb://%s:%s@%s:%s/%s' \
    % (_MONGODB_USER, _MONGODB_PASSWD, _MONGODB_HOST, _MONGODB_PORT, _MONGODB_NAME)

#Trying MongoMock for CI testig instead of real test DB
try:
	mongoengine.connect(_MONGODB_NAME, host= _MONGODB_DATABASE_HOST)
except Exception as e:
	logging.debug( '%s (%s)' % (e.message, type(e)))

########## END DATABASE CONFIGURATION

# override the mongodb with mocks for pytest
# mongoengine.register_connection(
#     'default',
#     name='test_iec',
#     host='mongomock://localhost',
#     # let datetime in pymongo/mongoengine with timezone information
#     tz_aware=True)

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#     }
# }
