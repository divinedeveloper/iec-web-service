from iec_lookup.services.iec_lookup_service import IECLookupService
from iec_lookup.tests.fixtures import mongo_test_db_setup, importer_exporter_code_details_as_json, importer_exporter_code_details_as_object, dgft_succes_response_html_string, dgft_error_response_html_string, iec_table_section_list, basic_iec_details_as_object, dgft_error_message
# from bs4 import BeautifulSoup, NavigableString, Tag
import bs4
from iec_lookup.models import ImporterExporterCodeDetails, Director, Branch, RegistrationDetails, RegistrationCumMembershipCertificateDetails, ImporterExporterCodeToBeRetrieved
from iec_lookup.custom_exceptions import CustomApiException
from django.conf import settings
from rest_framework import status
from collections import OrderedDict
import mock
from mock import MagicMock
import mongoengine
import pytest
from iec_lookup import utils
from pprint import pprint
from pytest_mock import mocker
import mongomock
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

@pytest.mark.integrationtest
@pytest.mark.usefixtures('mongo_test_db_setup')
class TestIntegrationIecLookupService:

	def setup_method(self):
		"""
		Initial data setup
		"""
		self.request_json = {'code': "1198002743",'name': "CAP"}
		self.non_existing_iec_json = {'code': "1298001743",'name': "PAC"}
		self.iec_lookup_service = IECLookupService()

	@pytest.mark.xfail(raises= requests.exceptions.ConnectionError, reason="DGFT site down")
	def test_integration_check_dgft_site_down(self):
		"""
		This method will tests poll_dgft_site_with_iec_and_name method in service
		check if dgft site is down and get ERROR
		assert message is ERROR then site is down else not
		"""
		dgft_site_response = self.iec_lookup_service.poll_dgft_site_with_iec_and_name(self.request_json)
		assert dgft_site_response != "ERROR"

	def test_integration_save_complete_iec_details(self, basic_iec_details_as_object, importer_exporter_code_details_as_object):
		"""
		This method will tests save_complete_iec_details method in service
		get all data and save in iec details document 
		assert  data is persisted
		"""
		saved_iec_details = self.iec_lookup_service.save_complete_iec_details(basic_iec_details_as_object,
			importer_exporter_code_details_as_object.directors,importer_exporter_code_details_as_object.branches,
			importer_exporter_code_details_as_object.registration_details,importer_exporter_code_details_as_object.rcmc_details)

		mongo_test_db_setup.document_id = saved_iec_details.id
		assert saved_iec_details.importer_exporter_code == basic_iec_details_as_object.importer_exporter_code
		assert basic_iec_details_as_object.party_name in saved_iec_details.party_name
		assert saved_iec_details.exporter_type != "" or None
		assert saved_iec_details.importer_exporter_code_status != "" or None
		assert saved_iec_details.nature_of_concern != "" or None



	def test_integration_get_iec_with_code_and_name(self):
		"""
		This method will tests get_iec_with_code_and_name method in service
		to check if dgft site is up and get data
		assert  data is returned as per request
		"""
		importer_exporter_code_details = self.iec_lookup_service.get_iec_with_code_and_name(self.request_json)

		assert importer_exporter_code_details.id == mongo_test_db_setup.document_id
		assert importer_exporter_code_details.importer_exporter_code == self.request_json['code']
		assert self.request_json['name'] in importer_exporter_code_details.party_name
		assert importer_exporter_code_details.exporter_type != "" or None
		assert importer_exporter_code_details.importer_exporter_code_status != "" or None
		assert importer_exporter_code_details.nature_of_concern != "" or None

	def test_integration_iec_with_code_and_name_not_in_db(self):
		"""
		This method will tests get_iec_with_code_and_name method in service
		to check if iec data is available in db
		assert  none is returned
		"""
		importer_exporter_code_details = self.iec_lookup_service.get_iec_with_code_and_name(self.non_existing_iec_json)

		assert importer_exporter_code_details == None


	def test_integration_save_iec_to_retrieve_data(self):
		"""
		This method will tests get_or_save_iec_to_retrieve_data method in service
		to check if dgft site is down save iec code and name to fetch data later
		assert  iec to be retrieved is persisted
		"""
		importer_exporter_code_to_retrieve = self.iec_lookup_service.get_or_save_iec_to_retrieve_data(self.non_existing_iec_json)

		mongo_test_db_setup.document_id = importer_exporter_code_to_retrieve.id
		assert importer_exporter_code_to_retrieve.importer_exporter_code == self.non_existing_iec_json['code']
		assert self.non_existing_iec_json['name'] == importer_exporter_code_to_retrieve.name
		assert importer_exporter_code_to_retrieve.is_iec_data_retrieved == False


	def test_integration_get_iec_to_retrieve_data(self):
		"""
		This method will tests get_or_save_iec_to_retrieve_data method in service
		to check if dgft site is down fetch iec code and name from iec to be retrieved
		assert  iec to be retrieved exists
		"""
		importer_exporter_code_to_retrieve = self.iec_lookup_service.get_or_save_iec_to_retrieve_data(self.non_existing_iec_json)

		assert importer_exporter_code_to_retrieve.id ==  mongo_test_db_setup.document_id
		assert importer_exporter_code_to_retrieve != None

	def test_integration_no_iec_with_code_and_name_in_db(self):
		"""
		This method will tests get_iec_with_code_and_name method in service
		to check if dgft site is up and get data
		assert  data is returned as per request
		"""
		importer_exporter_code_details = self.iec_lookup_service.get_iec_with_code_and_name(self.non_existing_iec_json)

		assert importer_exporter_code_details == None

	def test_integration_retrieve_iec_data_with_code(self):
		"""
		This method will tests retrieve_iec_data_with_code method in service
		to check if iec data is present in db
		assert  data is returned as per iec code
		"""
		importer_exporter_code_details = self.iec_lookup_service.retrieve_iec_data_with_code(self.request_json['code'])

		assert importer_exporter_code_details.importer_exporter_code == self.request_json['code']
		assert self.request_json['name'] in importer_exporter_code_details.party_name
		assert importer_exporter_code_details.exporter_type != "" or None
		assert importer_exporter_code_details.importer_exporter_code_status != "" or None
		assert importer_exporter_code_details.nature_of_concern != "" or None

	def test_integration_not_found_retrieve_iec_data_with_code(self):
		"""
		This method will tests retrieve_iec_data_with_code method in service
		assert  iec not found exception is raised
		"""
		with pytest.raises(CustomApiException) as exc_info:
			self.iec_lookup_service.retrieve_iec_data_with_code(self.non_existing_iec_json['code'])


	def teardown_method(self):
		"""
		Set values to none
		"""
		self.request_json = None
		self.non_existing_iec_json = None
		self.iec_lookup_service = None


