# from django.test import TestCase
from iec_lookup.utils import get_test_db
from iec.settings.local import _MONGODB_NAME, _MONGODB_DATABASE_HOST
from django.conf import settings
import mongoengine
import logging
import mock
import pytest
from iec_lookup import utils
from pytest_mock import mocker
import requests
import json
from mongomock import MongoClient
from pymongo.errors import InvalidURI 
# from iec_lookup.tests.fixtures import mongo_test_db_setup

# Create your tests here.

# Feature: To be able to do something
#   In order to do something
#   As someone
#   I want the system to do this thing

# Scenario: A sample one
#   Given this situation
#   When I do something
#   Then what I get is what I was expecting for


@pytest.mark.unittest
class TestUnitConnectionToTestDB:
	"""
	Testing util method get_test_db() which returns instance of
	Test database
	"""

	def setup_method(self):
		self.test_db_client = None

	def test_get_test_db_connection(self, mocker):
		"""
		get an test db client instance from connection pool
		check if it is valid instance of MongoClient
		"""

		mock_db_connection = mocker.patch.object(mongoengine, 'connect')
		mock_db_connection(db='test_iec', host='mongomock://localhost')
		db_connection = mocker.patch.object(mongoengine.connection,'get_connection')

		self.test_db_client = get_test_db()
		assert  isinstance(self.test_db_client, mock.mock.MagicMock)
		assert  isinstance(db_connection, mock.mock.MagicMock)

	def teardown_method(self):
		"""
		Close the local database connection
		if open due to errors or non execution of test_disconnecting_main_db()
		"""
		self.test_db_client.close()


@pytest.mark.unittest
class TestUnitNoConnectionToTestDB:
	"""
	Testing util method get_test_db() which cant connect to
	Test database
	"""

	def setup_method(self):
		self.test_db_client = None

	def test_db_connection_error(self, mocker):
		"""
		check when no connection params are present
		It will raise connection error
		"""

		mock_db_empty_connection = mocker.patch.object(mongoengine, 'connect')
		mock_disconnect = mocker.patch.object(mongoengine.connection,'disconnect')
		with pytest.raises(mongoengine.connection.MongoEngineConnectionError) as exc_info:
			mock_disconnect()
			mock_db_empty_connection.side_effect = mongoengine.connection.MongoEngineConnectionError()
			return mock_db_empty_connection()

	def test_invalid_uri_for_db_connection(self, mocker):
		"""
		check when an invalid URI is passed to connection
		InvalidUri error is raised
		"""

		mock_db_empty_connection = mocker.patch.object(mongoengine, 'connect')
		mock_disconnect = mocker.patch.object(mongoengine.connection,'disconnect')
		with pytest.raises(InvalidURI) as exc_info:
			mock_disconnect()
			mock_db_empty_connection.side_effect = InvalidURI()
			return mock_db_empty_connection(host="mongod://")

	def teardown_method(self):
		"""
		Close the local database connection
		if open due to errors or non execution of test_disconnecting_main_db()
		"""
		self.test_db_client = None

@pytest.mark.unittest
class TestUnitGlobalStringSettings:
	"""
	Testing util method get_test_db() which cant connect to
	Test database
	"""

	def setup_method(self):
		self.test_dgft_site_url = "http://dgft.delhi.nic.in:8100/dgft/IecPrint"
		self.test_iec_not_proper = "IEC is not proper"
		self.test_applicant_name_not_proper = "Applicant name is not proper"
		self.test_dgft_success_reply = "Importer Exporter Code"
 		self.test_party_name_address = "Party Name and Address" 
		self.test_banker_detail = "Banker Detail"
		self.test_iec_status = "IEC Status"

	def test_dgft_site_url_string(self):
		"""
		check if valid dgft site url in settings
		"""
		assert self.test_dgft_site_url == settings.DGFT_SITE_URL

	def test_iec_not_proper_string(self):
		"""
		check if valid test_iec_not_proper in settings
		"""
		assert self.test_iec_not_proper == settings.DGFT_IEC_NOT_PROPER_ERROR

	def test_applicant_name_not_proper_string(self):
		"""
		check if valid test_applicant_name_not_proper in settings
		"""
		assert self.test_applicant_name_not_proper == settings.DGFT_APPLICANT_NAME_NOT_PROPER_ERROR

	def test_dgft_success_reply_string(self):
		"""
		check if valid test_dgft_success_reply in settings
		"""
		assert self.test_dgft_success_reply == settings.DGFT_SUCCESS_REPLY

	def test_party_name_address_string(self):
		"""
		check if valid test_party_name_address in settings
		"""
		assert self.test_party_name_address == settings.DGFT_PARTY_NAME_ADDRESS_STRING

	def test_iec_not_proper_string(self):
		"""
		check if valid test_banker_detail in settings
		"""
		assert self.test_banker_detail == settings.DGFT_BANKER_DETAIL_STRING

	def test_iec_not_proper_string(self):
		"""
		check if valid test_iec_status in settings
		"""
		assert self.test_iec_status == settings.IEC_STATUS_STRING

	def teardown_method(self):
		"""
		Close the local database connection
		if open due to errors or non execution of test_disconnecting_main_db()
		"""
		self.test_dgft_site_url = None
		self.test_iec_not_proper = None
		self.test_applicant_name_not_proper = None
		self.test_dgft_success_reply = None
 		self.test_party_name_address = None
		self.test_banker_detail = None
		self.test_iec_status = None

	

		

