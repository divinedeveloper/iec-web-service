import pytest
import mongoengine
from iec_lookup.utils import get_test_db
from django.conf import settings
import logging


@pytest.fixture(scope='session')#class, module, session
def mongo_test_db_setup(request):
	"""
	Fixture for setting mongo test db which can be included in test methods
	eliminates need to write setup and teardown methods for db
	"""
	logging.debug("Creating a test database and getting connection...")
	test_db = get_test_db()
	yield test_db
	document_id = None
	logging.debug("Dropping a test database ...")
	test_db.drop_database(settings._MONGODB_NAME)
	logging.debug("Closing db connection ...")
	test_db.close()