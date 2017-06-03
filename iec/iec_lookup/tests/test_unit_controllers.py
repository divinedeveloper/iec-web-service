from rest_framework.test import APIRequestFactory, APIClient
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

@pytest.mark.unittest
class TestUnitIecLookupController:

	def setup_method(self):
		"""
		Get instance of APIRequestFactory
		To mock request object which will be directly passed to 
		views as a first argument
		"""
		self.request_factory = APIRequestFactory()
		self.validate_iec_api_url = reverse("validate_importer_exporter_code")
		self.retrieve_api_url = reverse("retrieve_importer_exporter_code")

	def test_unit_successful_lookup_iec_by_code_and_name(self, mocker, importer_exporter_code_details_as_object, importer_exporter_code_details_as_json):
		"""
		This method will tests validate_importer_exporter_code method in controller
		assert status is 200 and data is returned as per request
		"""

		request = self.request_factory.post(self.validate_iec_api_url, {'code': "1198002743",'name': "CAP"}, format='json')
		mocker.patch.object(IECLookupService, 'lookup_validate_iec')
		mocked_serializer = mocker.patch('iec_lookup.serializers.IECDetailsSerializer')
	
		response = validate_importer_exporter_code(request)

		IECLookupService.lookup_validate_iec.assert_called_with(json.loads(request.body))
		IECLookupService.lookup_validate_iec.return_value = importer_exporter_code_details_as_object
		mocked_serializer(importer_exporter_code_details_as_object)
		mocked_serializer.assert_called_with(importer_exporter_code_details_as_object)
		validate_importer_exporter_code.return_value = importer_exporter_code_details_as_json

		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_200_OK
		assert json_response['importer_exporter_code'] != "" or None
		assert json_response['party_name'] != "" or None 


	def test_unit_dgft_site_down(self, mocker):
		"""
		This method will tests validate_importer_exporter_code method in controller
		by mocking that lookup_validate_iec service method will throw dgft site down exception
		assert status is 503 and message is returned
		"""

		request = self.request_factory.post(self.validate_iec_api_url, {'code': "1198002743",'name': "CAP"}, format='json')

		mock_lookup_validate_iec = mocker.patch.object(IECLookupService, 'lookup_validate_iec')
		mocked_serializer = mocker.patch('iec_lookup.serializers.IECDetailsSerializer')
		mock_lookup_validate_iec.side_effect = CustomApiException(utils.DGFT_SITE_IS_DOWN, status.HTTP_503_SERVICE_UNAVAILABLE)
		response = validate_importer_exporter_code(request)
		IECLookupService.lookup_validate_iec.assert_called_with(json.loads(request.body))

		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
		assert json_response['message'] == utils.DGFT_SITE_IS_DOWN

	def test_unit_iec_code_not_proper_error_from_dgft_site(self, mocker):
		"""
		This method will tests validate_importer_exporter_code method in controller
		by mocking that lookup_validate_iec service method will throw iec code not proper error from dgft site
		assert status is 400 and message is returned
		"""

		request = self.request_factory.post(self.validate_iec_api_url, {'code': "1198012345",'name': "CAP"}, format='json')

		mock_lookup_validate_iec = mocker.patch.object(IECLookupService, 'lookup_validate_iec')
		mocked_serializer = mocker.patch('iec_lookup.serializers.IECDetailsSerializer')
		mock_lookup_validate_iec.side_effect = CustomApiException(utils.DGFT_SITE_IEC_CODE_NOT_PROPER, status.HTTP_400_BAD_REQUEST)
		response = validate_importer_exporter_code(request)
		IECLookupService.lookup_validate_iec.assert_called_with(json.loads(request.body))

		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['message'] == utils.DGFT_SITE_IEC_CODE_NOT_PROPER

	def test_unit_iec_name_not_proper_error_from_dgft_site(self, mocker):
		"""
		This method will tests validate_importer_exporter_code method in controller
		by mocking that lookup_validate_iec service method will throw iec name not proper error from dgft site
		assert status is 400 and message is returned
		"""

		request = self.request_factory.post(self.validate_iec_api_url, {'code': "1198002743",'name': "PAC"}, format='json')

		mock_lookup_validate_iec = mocker.patch.object(IECLookupService, 'lookup_validate_iec')
		mocked_serializer = mocker.patch('iec_lookup.serializers.IECDetailsSerializer')
		mock_lookup_validate_iec.side_effect = CustomApiException(utils.DGFT_SITE_IEC_NAME_NOT_PROPER, status.HTTP_400_BAD_REQUEST)
		response = validate_importer_exporter_code(request)
		IECLookupService.lookup_validate_iec.assert_called_with(json.loads(request.body))

		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['message'] == utils.DGFT_SITE_IEC_NAME_NOT_PROPER

	def test_unit_validate_iec_internal_server_error(self, mocker):
		"""
		This method will tests validate_importer_exporter_code method in controller
		by mocking that lookup_validate_iec service method will throw internal server error
		assert status is 500 and message is returned
		"""

		request = self.request_factory.post(self.validate_iec_api_url, {'code': "1198002743",'name': "CAP"}, format='json')

		mock_lookup_validate_iec = mocker.patch.object(IECLookupService, 'lookup_validate_iec')
		mocked_serializer = mocker.patch('iec_lookup.serializers.IECDetailsSerializer')
		mock_lookup_validate_iec.side_effect = Exception(utils.INTERNAL_SERVER_ERROR)
		response = validate_importer_exporter_code(request)
		IECLookupService.lookup_validate_iec.assert_called_with(json.loads(request.body))

		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
		assert json_response['message'] == utils.INTERNAL_SERVER_ERROR


	def test_unit_validate_iec_with_no_request_body(self, mocker):
		"""
		This method will tests validate_importer_exporter_code method in controller
		by not sending request body
		assert status is 400 and error message
		"""

		request = self.request_factory.post(self.validate_iec_api_url, format='json')

		response = validate_importer_exporter_code(request)

		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['message'] == utils.REQUEST_BODY_NOT_PROVIDED
	
	
	def test_unit_validate_iec_with_non_json_request_body(self, mocker):
		"""
		This method will tests validate_importer_exporter_code method in controller
		for non json request body 
		assert status is 400 and error message
		"""

		request = self.request_factory.post(self.validate_iec_api_url, {'code': "",'name': ""}, content_type='application/xml')

		response = validate_importer_exporter_code(request)
		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['message'] == utils.REQUEST_NON_JSON_FORMAT

	def test_unit_validate_iec_with_blank_json_data(self, mocker):
		"""
		This method will tests validate_importer_exporter_code method in controller
		for blank json values as request data 
		assert status is 400 and error message
		"""

		request = self.request_factory.post(self.validate_iec_api_url, {'code': "",'name': ""}, format='json')

		response = validate_importer_exporter_code(request)
		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['message'] == utils.MISSING_FIELD_VALUE + 'code' #"Please provide code"

		request = self.request_factory.post(self.validate_iec_api_url, {'code': "",'name': "CAP"}, format='json')

		response = validate_importer_exporter_code(request)
		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['message'] == utils.MISSING_FIELD_VALUE + 'code' #"Please provide code"

		request = self.request_factory.post(self.validate_iec_api_url, {'code': "1198002743",'name': ""}, format='json')

		response = validate_importer_exporter_code(request)
		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['message'] == utils.MISSING_FIELD_VALUE + 'name' #"Please provide code"

	def test_unit_validate_iec_with_invalid_iec_code(self):
		"""
		This method will tests validate_importer_exporter_code method in controller
		for invalid iec code in json request data 
		assert status is 400 and error message
		"""

		#test for invalid code number only.
		request = self.request_factory.post(self.validate_iec_api_url, {'code': "11980",'name': "CAP"}, format='json')
		response = validate_importer_exporter_code(request)
		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['message'] == utils.INVALID_IEC_CODE

	def test_unit_successful_retrieve_importer_exporter_code(self, mocker, importer_exporter_code_details_as_object, importer_exporter_code_details_as_json):
		"""
		This method will tests retrieve_importer_exporter_code method in controller
		assert status is 200 and data is returned as per request
		"""

		params = {'code': '1198002743'}
		request = self.request_factory.get(self.retrieve_api_url, params)
		mocker.patch.object(IECLookupService, 'retrieve_iec_data_with_code')
		mocked_serializer = mocker.patch('iec_lookup.serializers.IECDetailsSerializer')

		
		response = retrieve_importer_exporter_code(request)

		IECLookupService.retrieve_iec_data_with_code.assert_called_with(params['code'])
		IECLookupService.retrieve_iec_data_with_code.return_value = importer_exporter_code_details_as_object
		mocked_serialize_response = mocked_serializer(importer_exporter_code_details_as_object)
		mocked_serializer.assert_called_with(importer_exporter_code_details_as_object)
		retrieve_importer_exporter_code.return_value = importer_exporter_code_details_as_json

		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_200_OK
		assert json_response['importer_exporter_code'] != "" or None
		assert json_response['party_name'] != "" or None 


	def test_unit_validate_retrieve_iec_with_blank_code_param(self):
		"""
		This method will tests retrieve_importer_exporter_code method in controller
		for blank request code param
		assert status is 400 and error message
		"""

		params = {'code': ''}
		request = self.request_factory.get(self.retrieve_api_url, params)
		response = retrieve_importer_exporter_code(request)
		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['message'] == utils.INVALID_IEC_CODE


	def test_unit_validate_retrieve_iec_with_invalid_code_param(self):
		"""
		This method will tests retrieve_importer_exporter_code method in controller
		for invalid request code param
		assert status is 400 and error message
		"""
		params = {'code': '11980'}
		request = self.request_factory.get(self.retrieve_api_url, params)
		response = retrieve_importer_exporter_code(request)
		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert json_response['message'] == utils.INVALID_IEC_CODE

	def test_unit_iec_not_found(self, mocker):
		"""
		This method will tests retrieve_importer_exporter_code method in controller
		for valid request iec code(not in our db) param but not present in database
		assert status is 404 and error message
		"""
		params = {'code': '1198021324'}
		request = self.request_factory.get(self.retrieve_api_url, params)
		mock_retrieve_iec_data_with_code = mocker.patch.object(IECLookupService, 'retrieve_iec_data_with_code')
		mock_retrieve_iec_data_with_code.side_effect = CustomApiException(utils.IEC_NOT_FOUND_IN_DB, status.HTTP_404_NOT_FOUND)
		response = retrieve_importer_exporter_code(request)

		IECLookupService.retrieve_iec_data_with_code.assert_called_with(params['code'])
		json_response = json.loads(response.content)

		assert response.status_code == status.HTTP_404_NOT_FOUND
		assert json_response['message'] == utils.IEC_NOT_FOUND_IN_DB

	def teardown_method(self):
		"""
		Close the local database connection
		if open due to errors or non execution of test_disconnecting_main_db()
		"""
		self.request_factory = None
		self.validate_iec_api_url = None
		self.retrieve_api_url = None
