from rest_framework.test import APIClient
from rest_framework import status
from django.conf import settings
from iec_lookup.models import ImporterExporterCodeToBeRetrieved, ImporterExporterCodeDetails
from iec_lookup.services.iec_lookup_service import IECLookupService 
from iec_lookup.serializers import IECDetailsSerializer
from iec_lookup.controllers.iec_lookup_controller import validate_importer_exporter_code, retrieve_importer_exporter_code
from iec_lookup.tests.fixtures import mongo_test_db_setup, importer_exporter_code_details_as_json, importer_exporter_code_details_as_object
from django.core.urlresolvers import reverse
from iec_lookup.custom_exceptions import CustomApiException
import mock
import pytest
from iec_lookup import utils
from pytest_mock import mocker
import requests
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

@pytest.mark.functionaltest
@pytest.mark.usefixtures('mongo_test_db_setup')
class TestIntegrationIecLookupController:

	def setup_method(self):
		"""
		Get instance of APIClient
		To make a dumbby browser like client request to our API's
		"""
		self.client = APIClient()

	def test_functional_successful_lookup_iec_by_code_and_name(self):
		"""
		This method will tests validate_importer_exporter_code method in controller
		using API client directly making client request and getting response
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

	def test_functional_get_iec_already_present_in_db_by_code_and_name(self):
		"""
		This method will tests validate_importer_exporter_code method in controller
		using API client directly making client request and getting response
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

	def test_functional_retrieve_iec_already_present_in_db_by_code_only(self):
		"""
		This method will tests retrieve_importer_exporter_code method in controller
		by passing only iec code
		assert status is 200 and data is returned as per request
		"""
		params = {'code': '1198002743'}
		response = self.client.get(settings.IEC_RETRIEVE_URL, params)

		json_response = json.loads(response.content)

		assert json_response['id'] == mongo_test_db_setup.document_id
		assert response.status_code == status.HTTP_200_OK
		assert json_response['importer_exporter_code'] == "1198002743"
		assert "CAP" in json_response['party_name']
		assert json_response['exporter_type'] != "" or None
		assert json_response['importer_exporter_code_status'] != "" or None
		assert json_response['nature_of_concern'] != "" or None

	
	def test_functional_validate_iec_by_invalid_iec_code(self):
		"""
		This method will tests validate_importer_exporter_code method in controller
		assert status is 200 and data is returned as per request
		"""
		response = self.client.post(settings.IEC_LOOKUP_URL, {'code': '11980','name': 'CAP'} , format='json')

		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['message'] == utils.INVALID_IEC_CODE

	def test_functional_validate_iec_by_blank_json_data(self):
		"""
		This method will tests validate_importer_exporter_code method in controller
		assert status is 200 and data is returned as per request
		"""
		response = self.client.post(settings.IEC_LOOKUP_URL, {'code': '','name': ''} , format='json')

		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['message'] == utils.MISSING_FIELD_VALUE + 'code'

	def test_functional_retrieve_importer_exporter_code_with_blank_code_param(self):
		"""
		This method will tests retrieve_importer_exporter_code method in controller
		for invalid request param
		assert status is 400 and error message
		"""
		#no code passed
		params = {'code': ''}
		response = self.client.get(settings.IEC_RETRIEVE_URL, params)

		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['message'] == utils.INVALID_IEC_CODE

	def test_functional_retrieve_importer_exporter_code_with_invalid_code_param(self):
		#invalid code passed
		params = {'code': '11980'}
		response = self.client.get(settings.IEC_RETRIEVE_URL, params)

		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['message'] == utils.INVALID_IEC_CODE

	def test_functional_retrieve_importer_exporter_code_with_iec_not_in_db(self):
		#valid code passed but iec data not available in db
		params = {'code': '1198021324'}
		response = self.client.get(settings.IEC_RETRIEVE_URL, params)

		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_404_NOT_FOUND
		assert json_response['message'] == utils.IEC_NOT_FOUND_IN_DB

	def test_functional_dgft_site_down_iec_saved_to_fetch_data_later(self, mocker):
		"""
		This method will tests if dgft site down
		assert status is 503 and record is saved in db
		"""

		#mock dgft site down and raise RequestException then normal code flow will happen
		mock_poll_dgft_site_with_iec_and_name = mocker.patch.object(IECLookupService, 'poll_dgft_site_with_iec_and_name')
		mock_poll_dgft_site_with_iec_and_name({'code': '0100000100','name': 'NATIONAL'})

		response = None
		mock_poll_dgft_site_with_iec_and_name.side_effect = requests.exceptions.RequestException()

		response = self.client.post(settings.IEC_LOOKUP_URL, {'code': '0100000100','name': 'NATIONAL'} , format='json')
		
		json_response = json.loads(response.content)
		importer_exporter_code_to_retrieve = ImporterExporterCodeToBeRetrieved.objects.get(importer_exporter_code= '0100000100', name__istartswith= 'NATIONAL')
		
		iec_to_be_retrieved = importer_exporter_code_to_retrieve

		assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
		assert iec_to_be_retrieved.importer_exporter_code == '0100000100'
		assert iec_to_be_retrieved.name == 'NATIONAL'
		assert iec_to_be_retrieved.is_iec_data_retrieved == False
		assert json_response['message'] == utils.DGFT_SITE_IS_DOWN

	@pytest.mark.xfail(raises= requests.exceptions.RequestException, reason="DGFT site down")
	def test_functional_lookup_dgft_site_down(self, mocker):
		"""
		This method will tests if dgft site down
		assert status is 503 and record is saved in db
		"""
		response = self.client.post(settings.IEC_LOOKUP_URL, {'code': '0100000100','name': 'NATIONAL'} , format='json')

		json_response = json.loads(response.content)

		assert response.status_code != status.HTTP_503_SERVICE_UNAVAILABLE


	def teardown_method(self):
		"""
		SET APIClient instance to none
		"""
		self.client = None



