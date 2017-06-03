import mongoengine
import logging
from django.conf import settings
from datetime import datetime


########## START EXCEPTION STRING MESSAGES CONFIGURATION

REQUEST_BODY_NOT_PROVIDED = "Please provide iec code and name in request body"
REQUEST_NON_JSON_FORMAT = "Please provide request body as json format only"
MISSING_FIELD_VALUE = "Please provide "
INVALID_IEC_CODE = "Please provide valid 10 digit iec code"
DGFT_SITE_IS_DOWN = "Sorry, Unable to connect to DGFT site. Please try again later." 
DGFT_SITE_IEC_CODE_NOT_PROPER = "Please enter proper iec code"
DGFT_SITE_IEC_NAME_NOT_PROPER = "Please enter proper iec name"
INTERNAL_SERVER_ERROR = "Oops, An Error occured"
IEC_NOT_FOUND_IN_DB = "Sorry, No IEC data found for given code."
DGFT_SITE_HTML_ERROR_RESPONSE = "The name Given By you does not match with the data OR you have entered less than three letters "

########## END EXCEPTION STRING MESSAGES CONFIGURATION



def get_real_test_db_connection():
	"""
	This method returns a mongodb connection for test database(for test) from connection pool
	"""
	try:
		mongoengine.connect(settings._MONGODB_NAME, host= settings._MONGODB_DATABASE_HOST)
		connect_db = mongoengine.connection.get_connection()
		return connect_db
	except Exception as e:
		logging.debug( '%s (%s)' % (e.message, type(e)))


def get_test_db():
	"""
	This method returns a Mongomock connection for database(for test) from connection pool
	"""
	try:
		mongoengine.connect('test_iec', host='mongomock://localhost')
		connect_db = mongoengine.connection.get_connection()	
		return connect_db
	except Exception as e:
		logging.debug( '%s (%s)' % (e.args, type(e)))
