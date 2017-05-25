import mongoengine
import logging
from django.conf import settings


def get_test_db():
	"""
	This method returns a mongodb connection for database(for test) from connection pool
	"""
	try:
		return mongoengine.connect(settings._MONGODB_NAME, host= settings._MONGODB_DATABASE_HOST)
	except Exception as e:
		logging.debug( '%s (%s)' % (e.message, type(e)))

