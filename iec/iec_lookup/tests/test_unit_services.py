from iec_lookup.services.iec_lookup_service import IECLookupService
from iec_lookup.tests.fixtures import mongo_test_db_setup, importer_exporter_code_details_as_json, importer_exporter_code_details_as_object, dgft_succes_response_html_string, dgft_error_response_html_string, iec_table_section_list, basic_iec_details_as_object, dgft_error_message
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

@pytest.mark.unittest
class TestIecLookupService:

	def setup_method(self):
		"""
		Get instance of API client
		"""
		self.request_json = {'code': "1198002743",'name': "CAP"}
		self.non_existing_iec_json = {'code': "1298001743",'name': "PAC"}
		self.iec_lookup_service = IECLookupService()
 
	
	def test_unit_lookup_iec_from_db(self, mocker, importer_exporter_code_details_as_object):
		"""
		This method will test lookup_validate_iec method in iec lookup service
		traversing the path - if iec data is present in db just return the object
		"""

		json_body = {'code': "1198002743",'name': "CAP"}
		mock_get_iec_code_name = mocker.patch.object(IECLookupService, 'get_iec_with_code_and_name')
		mock_get_iec_code_name(json_body)
		IECLookupService.get_iec_with_code_and_name.return_value = importer_exporter_code_details_as_object

		service_instant = IECLookupService()
		method_result = service_instant.lookup_validate_iec(json_body)

		IECLookupService.get_iec_with_code_and_name.assert_called_with(json_body)

		assert method_result != None
		assert method_result == IECLookupService.get_iec_with_code_and_name.return_value

	def test_unit_lookup_iec_by_successful_polling_dgft_site(self, mocker, importer_exporter_code_details_as_object, dgft_succes_response_html_string):
		"""
		This method will test lookup_validate_iec method in iec lookup service
		traversing the path - if iec data is NOT present in db  then
		Poll dgft site, fetch data, parse it and return iec data
		"""
		
		json_body = {'code': "1198002743",'name': "CAP"}
		mock_get_iec_code_name = mocker.patch.object(IECLookupService, 'get_iec_with_code_and_name')
		mock_get_iec_code_name(json_body)
		IECLookupService.get_iec_with_code_and_name.return_value = None
		mock_poll_dgft_site_with_iec_and_name = mocker.patch.object(IECLookupService, 'poll_dgft_site_with_iec_and_name')
		mock_poll_dgft_site_with_iec_and_name(json_body)
		IECLookupService.poll_dgft_site_with_iec_and_name.return_value = dgft_succes_response_html_string

		mock_handle_dgft_response = mocker.patch.object(IECLookupService, 'handle_dgft_response')
		mock_handle_dgft_response(IECLookupService.poll_dgft_site_with_iec_and_name.return_value)
		IECLookupService.handle_dgft_response.return_value = importer_exporter_code_details_as_object

		service_instant = IECLookupService()
		method_result = service_instant.lookup_validate_iec(json_body)

		IECLookupService.get_iec_with_code_and_name.assert_called_with(json_body)
		IECLookupService.poll_dgft_site_with_iec_and_name.assert_called_with(json_body)
		IECLookupService.handle_dgft_response.assert_called_with(IECLookupService.poll_dgft_site_with_iec_and_name.return_value)

		
		assert method_result != None
		assert method_result == IECLookupService.handle_dgft_response.return_value

	def test_unit_dgft_site_iec_code_not_proper_error(self, mocker):
		"""
		This method will test lookup_validate_iec method in iec lookup service
		traversing the path - if iec data is NOT present in db  then
		Poll dgft site, and it will return iec code not proper error
		"""
		
		json_body = {'code': "1198002743",'name': "CAP"}
		mock_get_iec_code_name = mocker.patch.object(IECLookupService, 'get_iec_with_code_and_name')
		mock_get_iec_code_name(json_body)
		IECLookupService.get_iec_with_code_and_name.return_value = None
		mock_poll_dgft_site_with_iec_and_name = mocker.patch.object(IECLookupService, 'poll_dgft_site_with_iec_and_name')
		mock_poll_dgft_site_with_iec_and_name(json_body)
		IECLookupService.poll_dgft_site_with_iec_and_name.return_value = settings.DGFT_IEC_NOT_PROPER_ERROR

		mock_handle_dgft_response = mocker.patch.object(IECLookupService, 'handle_dgft_response')

		with pytest.raises(CustomApiException) as exc_info:
			mock_handle_dgft_response.side_effect = CustomApiException(utils.DGFT_SITE_IEC_CODE_NOT_PROPER, status.HTTP_400_BAD_REQUEST)

			service_instant = IECLookupService()
			service_instant.lookup_validate_iec(json_body)

		IECLookupService.get_iec_with_code_and_name.assert_called_with(json_body)
		IECLookupService.poll_dgft_site_with_iec_and_name.assert_called_with(json_body)
		IECLookupService.handle_dgft_response.assert_called_with(IECLookupService.poll_dgft_site_with_iec_and_name.return_value)

	def test_unit_dgft_site_iec_name_not_proper_error(self, mocker):
		"""
		This method will test lookup_validate_iec method in iec lookup service
		traversing the path - if iec data is NOT present in db  then
		Poll dgft site, and it will return iec name not proper
		"""
		
		json_body = {'code': "1198002743",'name': "CAP"}
		mock_get_iec_code_name = mocker.patch.object(IECLookupService, 'get_iec_with_code_and_name')
		mock_get_iec_code_name(json_body)
		IECLookupService.get_iec_with_code_and_name.return_value = None
		mock_poll_dgft_site_with_iec_and_name = mocker.patch.object(IECLookupService, 'poll_dgft_site_with_iec_and_name')
		mock_poll_dgft_site_with_iec_and_name(json_body)
		IECLookupService.poll_dgft_site_with_iec_and_name.return_value = settings.DGFT_APPLICANT_NAME_NOT_PROPER_ERROR

		mock_handle_dgft_response = mocker.patch.object(IECLookupService, 'handle_dgft_response')

		with pytest.raises(CustomApiException) as exc_info:
			mock_handle_dgft_response.side_effect = CustomApiException(utils.DGFT_SITE_IEC_NAME_NOT_PROPER, status.HTTP_400_BAD_REQUEST)

			service_instant = IECLookupService()
			service_instant.lookup_validate_iec(json_body)

		IECLookupService.get_iec_with_code_and_name.assert_called_with(json_body)
		IECLookupService.poll_dgft_site_with_iec_and_name.assert_called_with(json_body)
		IECLookupService.handle_dgft_response.assert_called_with(IECLookupService.poll_dgft_site_with_iec_and_name.return_value)


	def test_unit_dgft_site_html_error_response(self, mocker):
		"""
		This method will test lookup_validate_iec method in iec lookup service
		traversing the path - if iec data is NOT present in db  then
		Poll dgft site, and it will return HTML error response string
		"""
		
		json_body = {'code': "1198002743",'name': "CAP"}
		mock_get_iec_code_name = mocker.patch.object(IECLookupService, 'get_iec_with_code_and_name')
		mock_get_iec_code_name(json_body)
		IECLookupService.get_iec_with_code_and_name.return_value = None
		mock_poll_dgft_site_with_iec_and_name = mocker.patch.object(IECLookupService, 'poll_dgft_site_with_iec_and_name')
		mock_poll_dgft_site_with_iec_and_name(json_body)
		IECLookupService.poll_dgft_site_with_iec_and_name.return_value = utils.DGFT_SITE_HTML_ERROR_RESPONSE

		mock_handle_dgft_response = mocker.patch.object(IECLookupService, 'handle_dgft_response')

		with pytest.raises(CustomApiException) as exc_info:
			mock_handle_dgft_response.side_effect = CustomApiException(utils.DGFT_SITE_HTML_ERROR_RESPONSE, status.HTTP_400_BAD_REQUEST)

			service_instant = IECLookupService()
			service_instant.lookup_validate_iec(json_body)

		IECLookupService.get_iec_with_code_and_name.assert_called_with(json_body)
		IECLookupService.poll_dgft_site_with_iec_and_name.assert_called_with(json_body)
		IECLookupService.handle_dgft_response.assert_called_with(IECLookupService.poll_dgft_site_with_iec_and_name.return_value)


	def test_unit_dgft_site_down(self, mocker):
		"""
		This method will test lookup_validate_iec method in iec lookup service
		traversing the path - if iec data is NOT present in db  then
		Poll dgft site, and it will return connection error or will be down
		"""
		
		json_body = {'code': "1198002743",'name': "CAP"}
		mock_get_iec_code_name = mocker.patch.object(IECLookupService, 'get_iec_with_code_and_name')
		mock_get_iec_code_name(json_body)
		IECLookupService.get_iec_with_code_and_name.return_value = None
		mock_poll_dgft_site_with_iec_and_name = mocker.patch.object(IECLookupService, 'poll_dgft_site_with_iec_and_name')
		mock_poll_dgft_site_with_iec_and_name(json_body)

		mock_get_or_save_iec_to_retrieve_data = mocker.patch.object(IECLookupService, 'get_or_save_iec_to_retrieve_data')
		mock_get_or_save_iec_to_retrieve_data(json_body)

		with pytest.raises(CustomApiException) as exc_info:
			mock_poll_dgft_site_with_iec_and_name.side_effect = CustomApiException(utils.DGFT_SITE_IS_DOWN, status.HTTP_503_SERVICE_UNAVAILABLE)

			service_instant = IECLookupService()
			service_instant.lookup_validate_iec(json_body)

		IECLookupService.get_iec_with_code_and_name.assert_called_with(json_body)
		IECLookupService.poll_dgft_site_with_iec_and_name.assert_called_with(json_body)
		IECLookupService.get_or_save_iec_to_retrieve_data.assert_called_with(json_body)


	def test_unit_poll_dgft_site_with_iec_and_name(self, mocker):
		"""
		This method will tests poll_dgft_site_with_iec_and_name method in service
		to check if dgft site is up and get data
		assert status is 200 and data is returned as per request
		"""
		json_body = {'iec': "1198002743",'name': "CAP"}
		mock_requests_post_method = mocker.patch.object(requests, 'post')

		mock_dgft_response = mock_requests_post_method(settings.DGFT_SITE_URL , data= json_body).text

		service_instant = IECLookupService()
		dgft_response = service_instant.poll_dgft_site_with_iec_and_name(self.request_json)

		requests.post.assert_called_with(settings.DGFT_SITE_URL, data= json_body)

		assert mock_dgft_response == dgft_response


	def test_unit_handle_dgft_response_iec_code_not_proper(self):
		"""
		This method will test handle_dgft_response method in iec lookup service
		traversing the path - if dgft_site_response is iec code  not proper
		raise cutom api exception
		"""
		dgft_site_response = settings.DGFT_IEC_NOT_PROPER_ERROR
		with pytest.raises(CustomApiException) as exc_info:
			service_instant = IECLookupService()
			service_instant.handle_dgft_response(dgft_site_response)


	def test_unit_handle_dgft_response_iec_name_not_proper(self):
		"""
		This method will test handle_dgft_response method in iec lookup service
		traversing the path - if dgft_site_response is iec name not proper
		raise cutom api exception
		"""
		dgft_site_response = settings.DGFT_APPLICANT_NAME_NOT_PROPER_ERROR
		with pytest.raises(CustomApiException) as exc_info:
			service_instant = IECLookupService()
			service_instant.handle_dgft_response(dgft_site_response)

	def test_unit_handle_successful_dgft_response_(self, mocker, dgft_succes_response_html_string, importer_exporter_code_details_as_object):
		"""
		This method will tests poll_dgft_site_with_iec_and_name method in service
		to check if dgft site is up and get data
		assert data is returned as per request
		"""
		dgft_site_response = dgft_succes_response_html_string
		mock_html_to_object_parser_for_success_data_method = mocker.patch.object(IECLookupService, 'html_to_object_parser_for_success_data')

		mock_html_to_object_parser_for_success_data_method(dgft_site_response)
		mock_html_to_object_parser_for_success_data_method.return_value = importer_exporter_code_details_as_object

		service_instant = IECLookupService()
		dgft_response = service_instant.handle_dgft_response(dgft_site_response)

		mock_html_to_object_parser_for_success_data_method.assert_called_with(dgft_site_response)

		assert dgft_response == mock_html_to_object_parser_for_success_data_method.return_value

	def test_unit_handle_html_error_dgft_response_(self, mocker, dgft_error_response_html_string):
		"""
		This method will tests poll_dgft_site_with_iec_and_name method in service
		to check if dgft site is up and get data
		assert status is 400 and return message
		"""
		dgft_site_response = dgft_error_response_html_string
		mock_html_to_object_parser_for_error_data_method = mocker.patch.object(IECLookupService, 'html_to_object_parser_for_error_data')

		mock_html_to_object_parser_for_error_data_method(dgft_site_response)

		with pytest.raises(CustomApiException) as exc_info:
			mock_html_to_object_parser_for_error_data_method.side_effect = CustomApiException(utils.DGFT_SITE_HTML_ERROR_RESPONSE, status.HTTP_400_BAD_REQUEST)

			service_instant = IECLookupService()
			service_instant.html_to_object_parser_for_error_data(dgft_site_response)


		mock_html_to_object_parser_for_error_data_method.assert_called_with(dgft_site_response)

	def test_unit_html_to_object_parser_for_success_data(self, mocker, dgft_succes_response_html_string, importer_exporter_code_details_as_object, iec_table_section_list, basic_iec_details_as_object):
		"""
		This method will tests html_to_object_parser_for_success_data method in service
		Get success html data and send it to appropriate table data parser and get text values
		using BeautifulSoup library
		Then  save it
		assert return is importer_exporter_code_details_as_object
		"""
		dgft_site_response = dgft_succes_response_html_string
		mock_beautiful_soup= mocker.patch.object(bs4,'BeautifulSoup')
		mock_dgft_site_response_soup = mock_beautiful_soup(dgft_site_response, "html.parser")
		mock_find_all= mocker.patch.object(mock_dgft_site_response_soup,'find_all')
		mock_iec_tables_list = mock_find_all("table")
		mock_find_all.return_value = iec_table_section_list

		mock_iec_details_html_data_parser = mocker.patch.object(IECLookupService,'iec_details_html_data_parser')
		mock_importer_exporter_code_details = mock_iec_details_html_data_parser(mock_iec_tables_list[0])
		mock_iec_details_html_data_parser.return_value = basic_iec_details_as_object

		mock_directors_html_data_parser = mocker.patch.object(IECLookupService,'directors_html_data_parser')
		mock_directors_list = mock_directors_html_data_parser(mock_iec_tables_list[1])
		mock_directors_html_data_parser.return_value = importer_exporter_code_details_as_object.directors

		mock_branches_html_data_parser = mocker.patch.object(IECLookupService,'branches_html_data_parser')
		mock_branches_list = mock_branches_html_data_parser(mock_iec_tables_list[2])
		mock_branches_html_data_parser.return_value = importer_exporter_code_details_as_object.branches

		mock_registration_details_html_data_parser = mocker.patch.object(IECLookupService,'registration_details_html_data_parser')
		mock_registration_details_list = mock_registration_details_html_data_parser(mock_iec_tables_list[3])
		mock_registration_details_html_data_parser.return_value = importer_exporter_code_details_as_object.registration_details

		mock_rcmc_details_html_data_parser = mocker.patch.object(IECLookupService,'rcmc_details_html_data_parser')
		mock_rcmc_details_list = mock_rcmc_details_html_data_parser(mock_iec_tables_list[4])
		mock_rcmc_details_html_data_parser.return_value = importer_exporter_code_details_as_object.rcmc_details

		mock_save_complete_iec_details = mocker.patch.object(IECLookupService,'save_complete_iec_details')
		mock_saved_iec_details = mock_save_complete_iec_details(mock_importer_exporter_code_details, mock_directors_list, mock_branches_list, mock_registration_details_list, mock_rcmc_details_list)
		mock_save_complete_iec_details.return_value = importer_exporter_code_details_as_object

		service_instant = IECLookupService()
		saved_iec_details = service_instant.html_to_object_parser_for_success_data(dgft_site_response)

		
		mock_beautiful_soup.assert_called_with(dgft_site_response, "html.parser")
		mock_find_all.assert_called_with('table')
		IECLookupService.iec_details_html_data_parser.assert_called_with(iec_table_section_list[0])
		IECLookupService.directors_html_data_parser.assert_called_with(iec_table_section_list[1])
		IECLookupService.branches_html_data_parser.assert_called_with(iec_table_section_list[2])
		IECLookupService.registration_details_html_data_parser.assert_called_with(iec_table_section_list[3])
		IECLookupService.rcmc_details_html_data_parser.assert_called_with(iec_table_section_list[4])
		IECLookupService.save_complete_iec_details.assert_called_with(mock_iec_details_html_data_parser.return_value, 
			mock_directors_html_data_parser.return_value, mock_branches_html_data_parser.return_value, 
			mock_registration_details_html_data_parser.return_value, mock_rcmc_details_html_data_parser.return_value)
		assert saved_iec_details == mock_save_complete_iec_details.return_value


	def test_unit_html_to_object_parser_for_error_data(self, mocker, dgft_error_response_html_string, dgft_error_message):
		"""
		This method will tests html_to_object_parser_for_error_data method in service
		Get error html data and using BeautifulSoup library
		get error message and throw exception
		assert api exception is thrown
		"""

		dgft_site_error_response = dgft_error_response_html_string
		mock_beautiful_soup= mocker.patch.object(bs4,'BeautifulSoup')
		mock_dgft_site_error_response_soup = mock_beautiful_soup(dgft_site_error_response, "html.parser")
		mock_find = mocker.patch.object(mock_dgft_site_error_response_soup,'find')
		mock_text = mocker.patch.object(mock_find,'text')
		mock_dgft_error_message = mock_find("body").mock_text
		mock_dgft_error_message.return_value = dgft_error_message

		mock_html_to_object_parser_for_error_data = mocker.patch.object(IECLookupService, 'html_to_object_parser_for_error_data')

		with pytest.raises(CustomApiException) as exc_info:
			mock_html_to_object_parser_for_error_data.side_effect = CustomApiException(dgft_error_message, status.HTTP_400_BAD_REQUEST)

			service_instant = IECLookupService()
			service_instant.html_to_object_parser_for_error_data(dgft_site_error_response)

	def test_unit_iec_details_html_data_parser(self, mocker, basic_iec_details_as_object, iec_table_section_list):
		"""
		This method will test iec_details_html_data_parser in iec lookup service
		Get iec basic details html data 
		Parse and set in Iec object
		return iec object
		"""
		iec_html_data = iec_table_section_list[0]

		service_instant = IECLookupService()
		method_result = service_instant.iec_details_html_data_parser(iec_html_data)

		assert method_result != None
		assert type(method_result) is type(basic_iec_details_as_object) 

	def test_unit_parse_party_name_address_soup(self, mocker, basic_iec_details_as_object):
		"""
		This method will test parse_party_name_address_soup in iec lookup service
		Get partyname address html data 
		Parse and set in an ordered dict
		return dict
		"""
		party_name_address_html = """<td align="LEFT" colspan="50" valign="TOP">CAP &amp; SEAL (INDORE) PVT.LTD.,                     <br/>PLOT NO.5, FLAT NO.302, 3RD FLOOR, <br/>SHREE BALAJI HEIGHTS, RAJGARH KOTHI<br/>MANORAMAGANJ, INDORE, M.P.         <br/>PIN-452001<br/></td>"""
		party_name_address_soup = bs4.BeautifulSoup(party_name_address_html, "html.parser")

		iec_ordered_dict = OrderedDict([])

		service_instant = IECLookupService()
		party_name_address_dict = service_instant.parse_party_name_address_soup(party_name_address_soup, iec_ordered_dict)

		assert party_name_address_dict != None
		assert str(party_name_address_dict['party_name']).strip() == basic_iec_details_as_object.party_name
		assert str(party_name_address_dict['party_address']).strip()  == basic_iec_details_as_object.party_address

	def test_unit_parse_banker_detail_soup(self, basic_iec_details_as_object):
		"""
		This method will test parse_banker_detail_soup in iec lookup service
		Get banker detail html data 
		Parse and set data in an ordered dict
		return dict
		"""

		banker_detail_html = """<td align="LEFT" colspan="50" valign="TOP">STATE BANK OF INDORE, PITHAMPUR BRANCH, PITHAMPUR, DIST.DHAR.         <br/>A/C Type:1 CA                  <br/>A/C No  :CC 52               <br/></td>"""
		banker_detail_soup = bs4.BeautifulSoup(banker_detail_html, "html.parser")

		iec_ordered_dict = OrderedDict([])

		service_instant = IECLookupService()
		banker_detail_dict = service_instant.parse_banker_detail_soup(banker_detail_soup, iec_ordered_dict)

		assert banker_detail_dict != None
		assert str(banker_detail_dict['bank_name_and_location']).strip() == basic_iec_details_as_object.bank_name_and_location
		assert str(banker_detail_dict['account_type']).strip()  == basic_iec_details_as_object.account_type
		assert str(banker_detail_dict['account_number']).strip()  == basic_iec_details_as_object.account_number

	def test_unit_directors_html_data_parser(self, mocker, importer_exporter_code_details_as_object, iec_table_section_list):
		"""
		This method will test iec_details_html_data_parser in iec lookup service
		Get directors html data 
		Parse and set in directors object
		return directors list
		"""
		directors_html_data = iec_table_section_list[1]

		service_instant = IECLookupService()
		directors_list = service_instant.directors_html_data_parser(directors_html_data)

		assert len(directors_list) != 0
		assert directors_list == importer_exporter_code_details_as_object.directors
		assert directors_list[0] == importer_exporter_code_details_as_object.directors[0]

	def test_unit_branches_html_data_parser(self, mocker, importer_exporter_code_details_as_object, iec_table_section_list):
		"""
		This method will test branches_html_data_parser in iec lookup service
		Get branches html data 
		Parse and set in  object
		return branches list
		"""
		branches_html_data = iec_table_section_list[2]

		service_instant = IECLookupService()
		branches_list = service_instant.branches_html_data_parser(branches_html_data)

		assert len(branches_list) != 0
		assert branches_list == importer_exporter_code_details_as_object.branches
		assert branches_list[0] == importer_exporter_code_details_as_object.branches[0]

	def test_unit_parse_address_of_party_and_branch(self, mocker, basic_iec_details_as_object, importer_exporter_code_details_as_object):
		"""
		This method will test parse_address_of_party_and_branch in iec lookup service
		Get party_name_address_soup html data 
		Parse and assert address as basic_iec_details_as_object party_address
		"""
		party_name_address_html = """<td align="LEFT" colspan="50" valign="TOP">CAP &amp; SEAL (INDORE) PVT.LTD.,                     <br/>PLOT NO.5, FLAT NO.302, 3RD FLOOR, <br/>SHREE BALAJI HEIGHTS, RAJGARH KOTHI<br/>MANORAMAGANJ, INDORE, M.P.         <br/>PIN-452001<br/></td>"""
		party_name_address_soup = bs4.BeautifulSoup(party_name_address_html, "html.parser")

		service_instant = IECLookupService()
		address = service_instant.parse_address_of_party_and_branch(party_name_address_soup)

		assert address != None or ""
		assert address == basic_iec_details_as_object.party_address

		branch_address_html = """<TABLE BORDER=1><TR><TD VALIGN= TOP ALIGN=LEFT COLSPAN=50>1.</TD><TD VALIGN= TOP ALIGN=LEFT COLSPAN=100>Branch Code:1<BR>PLOT NO.184, ROAD NO.8,            <BR>SECTOR-1, PITHAMPUR,               <BR>DIST. DHAR, M.P.                   <BR>PIN-454775</TD></TR></TABLE>"""
		branch_address_html_soup = bs4.BeautifulSoup(branch_address_html, "html.parser")
		branches_data_list = branch_address_html_soup.find_all('td', attrs={'colspan':'100'})

		address = service_instant.parse_address_of_party_and_branch(branches_data_list[0])
		assert address != None or ""
		assert address == importer_exporter_code_details_as_object.branches[0].address


	def test_unit_registration_details_html_data_parser(self, mocker, importer_exporter_code_details_as_object, iec_table_section_list):
		"""
		This method will test registration_details_html_data_parser in iec lookup service
		Get registration_details html data 
		Parse and set in  object
		return registration_details_list
		"""
		registration_details_html_data = iec_table_section_list[3]

		service_instant = IECLookupService()
		registration_details_list = service_instant.registration_details_html_data_parser(registration_details_html_data)

		assert len(registration_details_list) != 0
		assert registration_details_list == importer_exporter_code_details_as_object.registration_details
		assert registration_details_list[0] == importer_exporter_code_details_as_object.registration_details[0]

	def test_unit_rcmc_details_html_data_parser(self, mocker, importer_exporter_code_details_as_object, iec_table_section_list):
		"""
		This method will test registration_details_html_data_parser in iec lookup service
		Get registration_details html data 
		Parse and set in  object
		assert registration_details_list
		"""
		rcmc_details_html_data = iec_table_section_list[4]

		service_instant = IECLookupService()
		rcmc_details_list = service_instant.rcmc_details_html_data_parser(rcmc_details_html_data)

		assert len(rcmc_details_list) != 0
		assert rcmc_details_list == importer_exporter_code_details_as_object.rcmc_details
		assert rcmc_details_list[0] == importer_exporter_code_details_as_object.rcmc_details[0]


	def test_unit_get_text_of_next_sibling(self, basic_iec_details_as_object):
		"""
		This method will test get_text_of_next_sibling in iec lookup service
		Get html data  soup
		Parse and get TEXT of next sibling
		assert TEXT of next sibling
		"""
		banker_detail_html = """<td align="LEFT" colspan="50" valign="TOP">STATE BANK OF INDORE, PITHAMPUR BRANCH, PITHAMPUR, DIST.DHAR.         <br/>A/C Type:1 CA                  <br/>A/C No  :CC 52               <br/></td>"""
		banker_detail_soup = bs4.BeautifulSoup(banker_detail_html, "html.parser")

		bank_name_and_location = banker_detail_soup.br.previous_sibling if banker_detail_soup.br.previous_sibling else "" 
		account_type = banker_detail_soup.br.next_sibling

		service_instant = IECLookupService()
		account_number = service_instant.get_text_of_next_sibling(account_type)

		assert account_number != None
		assert str(account_number).strip().split(":")[1] == basic_iec_details_as_object.account_number

	def test_unit_get_string_from_sibling_text(self, basic_iec_details_as_object):
		"""
		This method will test get_string_from_sibling_text in iec lookup service
		Get html text with void spaces
		Parse and remove void spaces, tabs
		assert trimmed/stripped TEXT
		"""
		banker_detail_html = """<td align="LEFT" colspan="50" valign="TOP">STATE BANK OF INDORE, PITHAMPUR BRANCH, PITHAMPUR, DIST.DHAR.         <br/>A/C Type:1 CA                  <br/>A/C No  :CC 52               <br/></td>"""
		banker_detail_soup = bs4.BeautifulSoup(banker_detail_html, "html.parser")

		bank_name_and_location = banker_detail_soup.br.previous_sibling if banker_detail_soup.br.previous_sibling else "" 
		account_type = banker_detail_soup.br.next_sibling

		service_instant = IECLookupService()
		stripped_account_type = service_instant.get_string_from_sibling_text(account_type)

		assert stripped_account_type == str(account_type).strip()


	def teardown_method(self):
		"""
		Set values to none
		"""
		self.request_json = None
		self.non_existing_iec_json = None
		self.iec_lookup_service = None


