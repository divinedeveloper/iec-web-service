from iec_lookup.services.iec_lookup_service import IECLookupService
from iec_lookup.tests.fixtures import mongo_test_db_setup
from bs4 import BeautifulSoup, NavigableString, Tag
from django.conf import settings
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
class TestIecLookupService:

	def setup_method(self):
		"""
		Get instance of API client
		"""
		self.request_json = {'code': "1198002743",'name': "CAP"}
		self.non_existing_iec_json = {'code': "1298001743",'name': "PAC"}
		self.iec_lookup_service = IECLookupService()

	
	def test_unit_poll_dgft_site_with_iec_and_name(self):
		"""
		This method will tests poll_dgft_site_with_iec_and_name method in service
		to check if dgft site is up and get data
		assert status is 200 and data is returned as per request
		"""
		# iec_lookup_service = IECLookupService()
		dgft_site_response = self.iec_lookup_service.poll_dgft_site_with_iec_and_name(self.request_json)
		assert dgft_site_response != settings.DGFT_IEC_NOT_PROPER_ERROR
		assert dgft_site_response != settings.DGFT_APPLICANT_NAME_NOT_PROPER_ERROR
		assert settings.DGFT_SUCCESS_REPLY in dgft_site_response
		assert bool(BeautifulSoup(dgft_site_response, "html.parser").find())

	@pytest.mark.xfail(raises= requests.exceptions.ConnectionError, reason="DGFT site down")
	def test_unit_check_dgft_site_down(self):
		"""
		This method will tests poll_dgft_site_with_iec_and_name method in service
		check if dgft site is down and get ERROR
		assert message is ERROR
		"""
		dgft_site_response = self.iec_lookup_service.poll_dgft_site_with_iec_and_name(self.request_json)
		assert dgft_site_response != "ERROR"

	def test_unit_get_iec_with_code_and_name(self):
		"""
		This method will tests get_iec_with_code_and_name method in service
		to check if dgft site is up and get data
		assert  data is returned as per request
		"""
		importer_exporter_code_details = self.iec_lookup_service.get_iec_with_code_and_name(self.request_json)
		importer_exporter_code_detail = importer_exporter_code_details[0]

		assert importer_exporter_code_detail.importer_exporter_code == self.request_json['code']
		assert self.request_json['name'] in importer_exporter_code_detail.party_name
		assert importer_exporter_code_detail.exporter_type != "" or None
		assert importer_exporter_code_detail.importer_exporter_code_status != "" or None
		assert importer_exporter_code_detail.nature_of_concern != "" or None

	def test_unit_no_iec_with_code_and_name_in_db(self):
		"""
		This method will tests get_iec_with_code_and_name method in service
		to check if dgft site is up and get data
		assert  data is returned as per request
		"""
		importer_exporter_code_details = self.iec_lookup_service.get_iec_with_code_and_name(self.non_existing_iec_json)
		logging.debug(importer_exporter_code_details)

		assert len(importer_exporter_code_details) == 0


	



