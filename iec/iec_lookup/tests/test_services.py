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

class TestIecLookupService:

	def setup_method(self):
		"""
		Get instance of API client
		"""
		self.request_json = {'code': "1198002743",'name': "CAP"}

	@pytest.mark.integrationtest
	def test_poll_dgft_site_with_iec_and_name(self):
		"""
		Integration Test
		This method will tests poll_dgft_site_with_iec_and_name method in service
		to check if dgft site is up and get data
		assert status is 200 and data is returned as per request
		"""
		iec_lookup_service = IECLookupService()
		dgft_site_response = iec_lookup_service.poll_dgft_site_with_iec_and_name(self.request_json)
		assert dgft_site_response != settings.DGFT_IEC_NOT_PROPER_ERROR
		assert dgft_site_response != settings.DGFT_APPLICANT_NAME_NOT_PROPER_ERROR
		assert settings.DGFT_SUCCESS_REPLY in dgft_site_response
		assert bool(BeautifulSoup(dgft_site_response, "html.parser").find())

	@pytest.mark.integrationtest
	@pytest.mark.xfail(raises= requests.exceptions.ConnectionError, reason="DGFT site down")
	def test_check_dgft_site_down(self):
		"""
		Integration Test
		This method will tests poll_dgft_site_with_iec_and_name method in service
		check if dgft site is down and get ERROR
		assert message is ERROR
		"""
		iec_lookup_service = IECLookupService()
		dgft_site_response = iec_lookup_service.poll_dgft_site_with_iec_and_name(self.request_json)
		assert dgft_site_response != "ERROR"



