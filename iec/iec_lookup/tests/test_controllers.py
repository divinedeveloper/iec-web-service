from rest_framework.test import APIRequestFactory
from rest_framework import status
from iec_lookup.controllers.iec_lookup_controller import validate_importer_exporter_code, retrieve_importer_exporter_code
from iec_lookup.tests.fixtures import mongo_test_db_setup
import pytest
import json
import logging

# Create your tests here.

# Feature: To be able to do something
#   In order to do something
#   As someone
#   I want the system to do this thing

# Scenario: A sample one
#   Given this situation
#   When I do something
#   Then what I get is what I was expecting for

# @pytest.mark.integrationtest
@pytest.mark.usefixtures('mongo_test_db_setup')
class TestIecLookupController:

	def setup_method(self):
		"""
		Get instance of API client
		"""
		self.request_factory = APIRequestFactory()
		# self.id = None


	def test_lookup_iec_by_code_and_name(self):
		"""
		Integration Test
		using fixtures for mongo test db
		This method will tests validate_importer_exporter_code method in controller
		assert status is 200 and data is returned as per request
		"""
		request = self.request_factory.post('/lookup/', {'code': "1198002743",'name': "CAP"}, format='json')
		response = validate_importer_exporter_code(request)
		json_response = json.loads(response.content)
		mongo_test_db_setup.document_id = json_response['id']
		assert response.status_code == status.HTTP_200_OK
		assert json_response['importer_exporter_code'] == "1198002743"
		assert "CAP" in json_response['party_name']
		assert json_response['exporter_type'] != "" or None
		assert json_response['importer_exporter_code_status'] != "" or None
		assert json_response['nature_of_concern'] != "" or None

	def test_get_iec_already_present_in_db_by_code_and_name(self):
		"""
		Integration Test
		using fixtures for mongo test db
		This method will tests validate_importer_exporter_code method in controller
		WITH iec data  already present in db and should not poll dgft site
		assert status is 200 and data is returned as per request
		"""
		request = self.request_factory.post('/lookup/', {'code': "1198002743",'name': "CAP"}, format='json')
		response = validate_importer_exporter_code(request)
		# logging.debug(response)
		logging.debug(type(response.content))
		logging.debug(response.content)
		json_response = json.loads(response.content)
		current_id = json_response['id']
		assert current_id == mongo_test_db_setup.document_id
		assert response.status_code == status.HTTP_200_OK
		assert json_response['importer_exporter_code'] == "1198002743"
		assert "CAP" in json_response['party_name']
		assert json_response['exporter_type'] != "" or None
		assert json_response['importer_exporter_code_status'] != "" or None
		assert json_response['nature_of_concern'] != "" or None

	def test_retrieve_iec_already_present_in_db_by_code_only(self):
		"""
		Integration Test
		using fixtures for mongo test db
		This method will tests retrieve_importer_exporter_code method in controller
		by passing only iec code
		assert status is 200 and data is returned as per request
		"""
		params = {'code': '1198002743'}
		request = self.request_factory.get('/retrieve/', params)
		response = retrieve_importer_exporter_code(request)
		json_response = json.loads(response.content)
		current_id = json_response['id']
		assert current_id == mongo_test_db_setup.document_id
		assert response.status_code == status.HTTP_200_OK
		assert json_response['importer_exporter_code'] == "1198002743"
		assert "CAP" in json_response['party_name']
		assert json_response['exporter_type'] != "" or None
		assert json_response['importer_exporter_code_status'] != "" or None
		assert json_response['nature_of_concern'] != "" or None


	def test_validate_importer_exporter_code_with_invalid_data(self):
		"""
		Integration Test
		using fixtures for mongo test db
		This method will tests validate_importer_exporter_code method in controller
		for invalid json request data 
		assert status is 400 and error message
		"""
		request = self.request_factory.post('/lookup/', {'code': "",'name': ""}, format='json')
		response = validate_importer_exporter_code(request)
		json_response = json.loads(response.content)
		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['detail'] == "Please provide code"

		#test for invalid code number only.
		request = self.request_factory.post('/lookup/', {'code': "11980",'name': "CAP"}, format='json')
		response = validate_importer_exporter_code(request)
		json_response = json.loads(response.content)
		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['detail'] == "Please provide valid 10 digit iec code"

	def test_retrieve_importer_exporter_code_with_invalid_data(self):
		"""
		Integration Test
		using fixtures for mongo test db
		This method will tests retrieve_importer_exporter_code method in controller
		for invalid request param
		assert status is 400 and error message
		"""
		#no code passed
		params = {'code': ''}
		request = self.request_factory.get('/retrieve/', params)
		response = retrieve_importer_exporter_code(request)
		json_response = json.loads(response.content)
		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['detail'] == "Please provide valid code"

		#invalid code passed
		params = {'code': '11980'}
		request = self.request_factory.get('/retrieve/', params)
		response = retrieve_importer_exporter_code(request)
		json_response = json.loads(response.content)
		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['detail'] == "Please provide valid code"

		#valid code passed but iec data not available in db
		params = {'code': '1198021324'}
		request = self.request_factory.get('/retrieve/', params)
		response = retrieve_importer_exporter_code(request)
		json_response = json.loads(response.content)
		assert response.status_code == status.HTTP_404_NOT_FOUND
		assert json_response['detail'] == "Sorry, No IEC data found for given code."


	def teardown_method(self):
		"""
		Close the local database connection
		if open due to errors or non execution of test_disconnecting_main_db()
		"""
		self.request_factory = None


