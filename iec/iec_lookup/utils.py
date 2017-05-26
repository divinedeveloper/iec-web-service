import mongoengine
import logging
from django.conf import settings


# def get_test_db():
# 	"""
# 	This method returns a mongodb connection for database(for test) from connection pool
# 	"""
# 	try:
# 		return mongoengine.connect(settings._MONGODB_NAME, host= settings._MONGODB_DATABASE_HOST)
# 	except Exception as e:
# 		logging.debug( '%s (%s)' % (e.message, type(e)))

# class MongoConnectionException(Exception):
#     """
#     Exception class to throw message if connection not successful
#     """

def get_test_db():
	"""
	This method returns a mongodb connection for database(for test) from connection pool
	"""
	try:
		mongoengine.connect('mongoenginetest', host='mongomock://localhost', alias='test_iec')
		connect_db = mongoengine.connection.get_connection('test_iec')	
		return connect_db
		# mongomock.MongoClient('['mongodb://localhost']', 27017)
		# return mongoengine.connect(settings._MONGODB_NAME, host= settings._MONGODB_DATABASE_HOST)
	except Exception as e:
		logging.debug( '%s (%s)' % (e.args, type(e)))

