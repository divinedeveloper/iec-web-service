from rest_framework.test import APIRequestFactory, APIClient
from rest_framework import status
from django.conf import settings
from iec_lookup.models import ImporterExporterCodeToBeRetrieved
from iec_lookup.controllers.iec_lookup_controller import validate_importer_exporter_code, retrieve_importer_exporter_code
from iec_lookup.tests.fixtures import mongo_test_db_setup
import requests
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

@pytest.mark.unittest
@pytest.mark.usefixtures('mongo_test_db_setup')
class TestUnitIecLookupController:

	def setup_method(self):
		"""
		Get instance of APIRequestFactory
		To mock request object which will be directly passed to 
		views as a first argument
		"""
		self.request_factory = APIRequestFactory()


	def test_unit_lookup_iec_by_code_and_name(self):
		"""
		This method will tests validate_importer_exporter_code method in controller
		assert status is 200 and data is returned as per request
		"""
		request = self.request_factory.post(settings.IEC_LOOKUP_MINI_URL, {'code': "1198002743",'name': "CAP"}, format='json')
		response = validate_importer_exporter_code(request)
		json_response = json.loads(response.content)
		mongo_test_db_setup.document_id = json_response['id']

		assert response.status_code == status.HTTP_200_OK
		assert json_response['importer_exporter_code'] == "1198002743"
		assert "CAP" in json_response['party_name']
		assert json_response['exporter_type'] != "" or None
		assert json_response['importer_exporter_code_status'] != "" or None
		assert json_response['nature_of_concern'] != "" or None

	def test_unit_get_iec_already_present_in_db_by_code_and_name(self):
		"""
		This method will tests validate_importer_exporter_code method in controller
		WITH iec data  already present in db and should not poll dgft site
		assert status is 200 and data is returned as per request
		"""
		request = self.request_factory.post(settings.IEC_LOOKUP_MINI_URL, {'code': "1198002743",'name': "CAP"}, format='json')
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

	def test_unit_retrieve_iec_already_present_in_db_by_code_only(self):
		"""
		This method will tests retrieve_importer_exporter_code method in controller
		by passing only iec code
		assert status is 200 and data is returned as per request
		"""
		params = {'code': '1198002743'}
		request = self.request_factory.get(settings.IEC_RETRIEVE_MINI_URL, params)
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


	def test_unit_validate_importer_exporter_code_with_blank_json_data(self):
		"""
		This method will tests validate_importer_exporter_code method in controller
		for invalid json request data 
		assert status is 400 and error message
		"""
		request = self.request_factory.post(settings.IEC_LOOKUP_MINI_URL, {'code': "",'name': ""}, format='json')
		response = validate_importer_exporter_code(request)
		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['detail'] == "Please provide code"

	def test_unit_validate_importer_exporter_code_with_invalid_iec_code(self):
		"""
		This method will tests validate_importer_exporter_code method in controller
		for invalid json request data 
		assert status is 400 and error message
		"""

		#test for invalid code number only.
		request = self.request_factory.post(settings.IEC_LOOKUP_MINI_URL, {'code': "11980",'name': "CAP"}, format='json')
		response = validate_importer_exporter_code(request)
		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['detail'] == "Please provide valid 10 digit iec code"

	def test_unit_retrieve_importer_exporter_code_with_blank_code_param(self):
		"""
		This method will tests retrieve_importer_exporter_code method in controller
		for invalid request param
		assert status is 400 and error message
		"""
		#no code passed
		params = {'code': ''}
		request = self.request_factory.get(settings.IEC_RETRIEVE_MINI_URL, params)
		response = retrieve_importer_exporter_code(request)
		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['detail'] == "Please provide valid code"

	def test_unit_retrieve_importer_exporter_code_with_invalid_code_param(self):
		#invalid code passed
		params = {'code': '11980'}
		request = self.request_factory.get(settings.IEC_RETRIEVE_MINI_URL, params)
		response = retrieve_importer_exporter_code(request)
		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['detail'] == "Please provide valid code"

	def test_unit_retrieve_importer_exporter_code_with_iec_not_in_db(self):
		#valid code passed but iec data not available in db
		params = {'code': '1198021324'}
		request = self.request_factory.get(settings.IEC_RETRIEVE_MINI_URL, params)
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


@pytest.mark.integrationtest
@pytest.mark.usefixtures('mongo_test_db_setup')
class TestIntegrationIecLookupController:

	def setup_method(self):
		"""
		Get instance of APIRequestFactory
		To mock request object which will be directly passed to 
		views as a first argument
		"""
		self.client = APIClient()
		# test_db.create_collection('importer_exporter_code_to_be_retrieved')

	def test_integration_lookup_iec_by_code_and_name(self):
		"""
		This method will tests validate_importer_exporter_code method in controller
		assert status is 200 and data is returned as per request
		"""
		response = self.client.post(settings.IEC_LOOKUP_URL, {'code': '1198002743','name': 'CAP'} , format='json')
		json_response = json.loads(response.content)
		mongo_test_db_setup.document_id = json_response['id']

		assert response.status_code == status.HTTP_200_OK
		assert json_response['importer_exporter_code'] == "1198002743"
		assert "CAP" in json_response['party_name']
		assert json_response['exporter_type'] != "" or None
		assert json_response['importer_exporter_code_status'] != "" or None
		assert json_response['nature_of_concern'] != "" or None

	def test_integration_get_iec_already_present_in_db_by_code_and_name(self):
		"""
		This method will tests validate_importer_exporter_code method in controller
		WITH iec data  already present in db and should not poll dgft site
		assert status is 200 and data is returned as per request
		"""
		response = self.client.post(settings.IEC_LOOKUP_URL, {'code': "1198002743",'name': "CAP"}, format='json')
		json_response = json.loads(response.content)

		assert json_response['id'] == mongo_test_db_setup.document_id
		assert response.status_code == status.HTTP_200_OK
		assert json_response['importer_exporter_code'] == "1198002743"
		assert "CAP" in json_response['party_name']
		assert json_response['exporter_type'] != "" or None
		assert json_response['importer_exporter_code_status'] != "" or None
		assert json_response['nature_of_concern'] != "" or None

	def test_integration_retrieve_iec_already_present_in_db_by_code_only(self):
		"""
		This method will tests retrieve_importer_exporter_code method in controller
		by passing only iec code
		assert status is 200 and data is returned as per request
		"""
		params = {'code': '1198002743'}
		response = self.client.get(settings.IEC_RETRIEVE_URL, params)
		json_response = json.loads(response.content)

		logging.debug(response)
		logging.debug(type(response.content))
		logging.debug(response.content)

		assert json_response['id'] == mongo_test_db_setup.document_id
		assert response.status_code == status.HTTP_200_OK
		assert json_response['importer_exporter_code'] == "1198002743"
		assert "CAP" in json_response['party_name']
		assert json_response['exporter_type'] != "" or None
		assert json_response['importer_exporter_code_status'] != "" or None
		assert json_response['nature_of_concern'] != "" or None


	
	def test_integration_validate_iec_by_invalid_iec_code(self):
		"""
		This method will tests validate_importer_exporter_code method in controller
		assert status is 200 and data is returned as per request
		"""
		response = self.client.post(settings.IEC_LOOKUP_URL, {'code': '11980','name': 'CAP'} , format='json')
		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['detail'] == "Please provide valid 10 digit iec code"

	def test_integration_validate_iec_by_blank_json_data(self):
		"""
		This method will tests validate_importer_exporter_code method in controller
		assert status is 200 and data is returned as per request
		"""
		response = self.client.post(settings.IEC_LOOKUP_URL, {'code': '','name': ''} , format='json')
		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['detail'] == "Please provide code"

	def test_integration_retrieve_importer_exporter_code_with_blank_code_param(self):
		"""
		This method will tests retrieve_importer_exporter_code method in controller
		for invalid request param
		assert status is 400 and error message
		"""
		#no code passed
		params = {'code': ''}
		response = self.client.get(settings.IEC_RETRIEVE_URL, params)
		json_response = json.loads(response.content)

		logging.debug(response)
		logging.debug(type(response.content))
		logging.debug(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['detail'] == "Please provide valid code"

	def test_integration_retrieve_importer_exporter_code_with_invalid_code_param(self):
		#invalid code passed
		params = {'code': '11980'}
		response = self.client.get(settings.IEC_RETRIEVE_URL, params)
		json_response = json.loads(response.content)

		logging.debug(response)
		logging.debug(type(response.content))
		logging.debug(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['detail'] == "Please provide valid code"

	def test_integration_retrieve_importer_exporter_code_with_iec_not_in_db(self):
		#valid code passed but iec data not available in db
		params = {'code': '1198021324'}
		response = self.client.get(settings.IEC_RETRIEVE_URL, params)
		json_response = json.loads(response.content)

		logging.debug(response)
		logging.debug(type(response.content))
		logging.debug(response.content)

		assert response.status_code == status.HTTP_404_NOT_FOUND
		assert json_response['detail'] == "Sorry, No IEC data found for given code."

	# @pytest.mark.xfail(raises= requests.exceptions.RequestException, reason="DGFT site down")
	# def test_integration_lookup_dgft_site_down(self):
	# 	"""
	# 	This method will tests if dgft site down
	# 	assert status is 503 and record is saved in db
	# 	"""
	# 	response = self.client.post(settings.IEC_LOOKUP_URL, {'code': '0100000100','name': 'NATIONAL'} , format='json')
	# 	json_response = json.loads(response.content)

	# 	importer_exporter_code_to_retrieve = ImporterExporterCodeToBeRetrieved.objects(importer_exporter_code= '0100000100', name__istartswith= 'NATIONAL')

	# 	logging.debug(importer_exporter_code_to_retrieve)
	# 	logging.debug(type(importer_exporter_code_to_retrieve))
	# 	iec_to_be_retrieved = importer_exporter_code_to_retrieve[0]

	# 	assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
	# 	assert iec_to_be_retrieved.importer_exporter_code == '0100000100'
	# 	assert json_response['detail'] == 'Sorry, Unable to connect to DGFT site. Please try again later.'


	def teardown_method(self):
		"""
		SET none to APIClient instance
		"""
		self.client = None
		# test_db.drop_collection('importer_exporter_code_to_be_retrieved')



