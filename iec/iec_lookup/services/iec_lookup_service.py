from django.shortcuts import render
from iec_lookup.models import ImporterExporterCodeDetails, Director, Branch, RegistrationDetails, RegistrationCumMembershipCertificateDetails, ImporterExporterCodeToBeRetrieved
from django.conf import settings
from rest_framework import status
from bs4 import BeautifulSoup, NavigableString, Tag
from collections import OrderedDict
from iec_lookup.custom_exceptions import CustomApiException
from iec_lookup import utils
import datetime
import requests
import logging
import json


# from estimate.constants import dgft_site_url

class IECLookupService():
	def __init__(self):
		return

	def lookup_validate_iec(self,json_body):
		"""
		arguments:
		json_body containing iec code and name

		returns iec_details or exception

		PSEUDOCODE:
		check if code and name exists in our db
		if yes return data 
		if no:
			poll dgft site
			check it is up or not(give exception message it is down, check later)
			if no:
				save iec code and name to get data later(give exception message it is down, check later)
			if yes:
				send iec code and name to dgft site 	
				check if it returns valid iec code and name
				if no:
					return message that it is not valid iec code and name
				if yes:
					Get data
					Parse html into object
					save to DB
					return data to user
		"""
		importer_exporter_code_details = self.get_iec_with_code_and_name(json_body)
		if importer_exporter_code_details:
			return importer_exporter_code_details
		else:
			try:
				dgft_site_response = self.poll_dgft_site_with_iec_and_name(json_body)
				#mocking success response if dgft site is down
				# dgft_site_response = settings.DGFT_SUCCESS_RESPONSE 
				return self.handle_dgft_response(dgft_site_response)
			except requests.exceptions.RequestException as e:
				#check if it exists in retrieval document, if not create one 
				importer_exporter_code_to_retrieve = self.get_or_save_iec_to_retrieve_data(json_body)
				raise CustomApiException(utils.DGFT_SITE_IS_DOWN, status.HTTP_503_SERVICE_UNAVAILABLE)

	def get_iec_with_code_and_name(self, json_body):
		"""
		This method will return a QuerySet List of IEC details
		Get object by code and name in calling method,
		will throw does not exists if objectiec not found
		"""
		try:
			importer_exporter_code_details = ImporterExporterCodeDetails.objects.get(importer_exporter_code= json_body["code"], party_name__istartswith= json_body["name"])
			return importer_exporter_code_details
		except ImporterExporterCodeDetails.DoesNotExist:
			importer_exporter_code_details = None
			return importer_exporter_code_details

	def poll_dgft_site_with_iec_and_name(self, json_body):
		"""
		This method will make a request to dgft site with provided code and name
		and fetch response
		"""
		dgft_site_response = requests.post(settings.DGFT_SITE_URL, data={'iec': json_body['code'], 'name': json_body['name']})
		return dgft_site_response.text

	def get_or_save_iec_to_retrieve_data(self, json_body):
		"""
		Save IEC to get data later
		Later a cronjob will regularly run to fetch data for IEC to be retireved and save in IEC details
		"""
		try:
			importer_exporter_code_to_retrieve = ImporterExporterCodeToBeRetrieved.objects.get(importer_exporter_code= json_body["code"], name__istartswith= json_body["name"])
			return importer_exporter_code_to_retrieve
		except ImporterExporterCodeToBeRetrieved.DoesNotExist:
			importer_exporter_code_to_retrieve = ImporterExporterCodeToBeRetrieved(importer_exporter_code= json_body["code"], name= json_body['name']).save()
			return importer_exporter_code_to_retrieve

	def handle_dgft_response(self, dgft_site_response):
		"""
		if invalid response from dgft site, throw exceptions with corresponding messages
		else send to parse html and get data
		"""
		if dgft_site_response == settings.DGFT_IEC_NOT_PROPER_ERROR:
			raise CustomApiException(utils.DGFT_SITE_IEC_CODE_NOT_PROPER, status.HTTP_400_BAD_REQUEST)

		if dgft_site_response == settings.DGFT_APPLICANT_NAME_NOT_PROPER_ERROR:
			raise CustomApiException(utils.DGFT_SITE_IEC_NAME_NOT_PROPER, status.HTTP_400_BAD_REQUEST)

		if settings.DGFT_SUCCESS_REPLY in dgft_site_response:
			#parse html and convert to json or dict and save in db
			return self.html_to_object_parser_for_success_data(dgft_site_response)
		else:
			#parse just the body of html of error message and throw exception message
			return self.html_to_object_parser_for_error_data(dgft_site_response)

	def html_to_object_parser_for_success_data(self, dgft_site_response):
		"""
		Get success html data and send it to appropriate table data parser and get text values
		using BeautifulSoup library
		Then  save it
		"""
		dgft_site_response_soup = BeautifulSoup(dgft_site_response, "html.parser")
		iec_tables = dgft_site_response_soup.find_all("table")
		importer_exporter_code_details = self.iec_details_html_data_parser(iec_tables[0])
		directors_list = self.directors_html_data_parser(iec_tables[1])
		branches_list = self.branches_html_data_parser(iec_tables[2])
		registration_details_list = self.registration_details_html_data_parser(iec_tables[3])
		rcmc_details_list = self.rcmc_details_html_data_parser(iec_tables[4])

		saved_iec_details = self.save_complete_iec_details(importer_exporter_code_details, directors_list, branches_list, registration_details_list, rcmc_details_list)
		return saved_iec_details

	def html_to_object_parser_for_error_data(self, dgft_site_error_response):
		""" 
		Some erros do come in html body parse them and throw message 
		"""
		dgft_site_error_response_soup = BeautifulSoup(dgft_site_error_response, "html.parser")
		dgft_site_error_message = str(dgft_site_error_response_soup.find("body").text)

		raise CustomApiException(dgft_site_error_message, status.HTTP_400_BAD_REQUEST)

	def iec_details_html_data_parser(self, iec_html_data):
		"""
		Table data for Basic IEC details,
		Parse and set in Iec object
		"""
		iec_table_rows = iec_html_data.find_all("tr")
		iec_order_dict_data = OrderedDict()

		for each_iec_row in iec_table_rows:
			if not each_iec_row.find_all('th'):
				iec_detail_key = each_iec_row.next_element.next_element

				if iec_detail_key != settings.DGFT_PARTY_NAME_ADDRESS_STRING and iec_detail_key != settings.DGFT_BANKER_DETAIL_STRING and iec_detail_key != settings.IEC_STATUS_STRING:
					#navigating to 3rd element to get value for key
					iec_detail_value = iec_detail_key.next_element.next_element.next_element.next_element
					#set ordered dict data
					iec_order_dict_data[iec_detail_key] = self.get_string_from_sibling_text(iec_detail_value)

				if iec_detail_key == settings.DGFT_PARTY_NAME_ADDRESS_STRING:
					party_name_address_soup = each_iec_row.find_all('td')[2]

					iec_order_dict_data = self.parse_party_name_address_soup(party_name_address_soup, iec_order_dict_data)

				if iec_detail_key == settings.IEC_STATUS_STRING:
					iec_status_soup = each_iec_row.find_all('td')[2]
					iec_status_value = iec_status_soup.b.text
					iec_order_dict_data[iec_detail_key] = self.get_string_from_sibling_text(iec_status_value)

				if iec_detail_key == settings.DGFT_BANKER_DETAIL_STRING:
					#get value explicitly
					banker_detail_soup = each_iec_row.find_all('td')[2]

					iec_order_dict_data = self.parse_banker_detail_soup(banker_detail_soup, iec_order_dict_data)
									
		
		importer_exporter_code_details = ImporterExporterCodeDetails(importer_exporter_code = iec_order_dict_data['IEC'],
			importer_exporter_code_allotment_date = iec_order_dict_data['IEC Allotment Date'],
			file_number = iec_order_dict_data['File Number'], file_date = iec_order_dict_data['File Date'], 
			party_name = iec_order_dict_data['party_name'],	party_address = iec_order_dict_data['party_address'],
			phone_number = iec_order_dict_data['Phone No'], email = iec_order_dict_data['e_mail'],
			exporter_type = iec_order_dict_data['Exporter Type'], importer_exporter_code_status = iec_order_dict_data['IEC Status'],
			date_of_establishment = iec_order_dict_data['Date of Establishment'], bin_pan_extension = iec_order_dict_data['BIN (PAN+Extension)'],
			pan_issue_date = iec_order_dict_data['PAN ISSUE DATE'], pan_issued_by = iec_order_dict_data['PAN ISSUED BY'],
			nature_of_concern = iec_order_dict_data['Nature Of Concern'], bank_name_and_location = iec_order_dict_data['bank_name_and_location'],
			account_type = iec_order_dict_data['account_type'], account_number = iec_order_dict_data['account_number'],
			is_active = True, is_deleted = False)

		return importer_exporter_code_details

	def parse_party_name_address_soup(self, party_name_address_soup, iec_order_dict_data):
		"""
		It separates party name and address fields and parses them
		"""
		party_name = party_name_address_soup.br.previous_sibling

		party_address = self.parse_address_of_party_and_branch(party_name_address_soup)

		iec_order_dict_data['party_name'] = self.get_string_from_sibling_text(party_name)
		iec_order_dict_data['party_address'] = party_address

		return iec_order_dict_data

	def parse_banker_detail_soup(self, banker_detail_soup, iec_order_dict_data):
		"""
		It separates bank name-location and account fields and parses them
		"""
		bank_name_and_location = banker_detail_soup.br.previous_sibling if banker_detail_soup.br.previous_sibling else "" 
		account_type = banker_detail_soup.br.next_sibling
		account_number = self.get_text_of_next_sibling(account_type)

		iec_order_dict_data['bank_name_and_location'] = self.get_string_from_sibling_text(bank_name_and_location)
		iec_order_dict_data['account_type'] = self.get_string_from_sibling_text( str(account_type).split(":")[1])
		iec_order_dict_data['account_number'] = self.get_string_from_sibling_text( str(account_number).split(":")[1])

		return iec_order_dict_data

	def directors_html_data_parser(self, directors_html_data):
		"""
		Table data for Directors,
		Parse and set in Director object
		"""
		directors_list = []
		directors_data = directors_html_data.find_all('td', attrs={'colspan':'100'})

		for each_director_data in directors_data:
			director_name = each_director_data.br.previous_sibling
			fathers_name = ""
			phone_email = ""
			address = ""

			list_of_br_tag = each_director_data.find_all("br")
			for index, each_br_tag in enumerate(list_of_br_tag):
				next_sibling_value = each_br_tag.next_sibling

				if next_sibling_value and next_sibling_value != " " and isinstance(next_sibling_value,NavigableString):
					next_sibling_value = self.get_string_from_sibling_text(next_sibling_value)

					#first field is father name value
					if index == 0:
						fathers_name = next_sibling_value
						continue

					#last field is phone/email value
					if index == len(list_of_br_tag)-1:
						phone_email = next_sibling_value.split(":")[1]
						continue

					#rest fields are of address
					if next_sibling_value.endswith(',') or 'PIN-' in next_sibling_value:
						#if string contains ',' or contain PIN no. that is end of string
						#then dont append comma with space
						if not 'PIN-' in next_sibling_value:
							#if string has ',' and is not PIN- number only append space
							address = address +  next_sibling_value + " "
						else:
							address = address +  next_sibling_value
					else:
						#append comma with space for displaying proper address
						next_sibling_value = next_sibling_value + ", "
						address = address +  next_sibling_value

			new_director = Director(name= self.get_string_from_sibling_text(director_name), fathers_name= self.get_string_from_sibling_text(fathers_name),
				address = self.get_string_from_sibling_text(address),
				phone_email = self.get_string_from_sibling_text(phone_email))

			directors_list.append(new_director) 
		return directors_list

	def branches_html_data_parser(self, branches_html_data):
		"""
		Table data for Branches,
		Parse and set in Branch object
		"""
		branches_list = []
		branches_data = branches_html_data.find_all('td', attrs={'colspan':'100'})

		for each_branch_data in branches_data:
			branch_code = str(each_branch_data.br.previous_sibling).split(":")[1]

			address = self.parse_address_of_party_and_branch(each_branch_data)

			new_branch = Branch(branch_code= int(branch_code), address = address)

			branches_list.append(new_branch)

		return branches_list
		
	def parse_address_of_party_and_branch(self, address_soup):
		"""
		This helper method takes table data containing address soup
		and iterates on all br tags to get address text, 
		append space and ',' for proper string formatting
		and returns address
		"""
		address = ""
		for each_br_tag in address_soup.find_all("br"):
			next_sibling_value = each_br_tag.next_sibling
			if next_sibling_value and next_sibling_value != " " and isinstance(next_sibling_value,NavigableString):
				next_sibling_value = self.get_string_from_sibling_text(next_sibling_value)
				if next_sibling_value.endswith(',') or 'PIN-' in next_sibling_value:
					#if string contains ',' or contain PIN no. that is end of string
					#then dont append comma with space
					if not 'PIN-' in next_sibling_value:
						#if string has ',' and is not PIN- number only append space
						address = address +  next_sibling_value + " "
					else:
						address = address +  next_sibling_value
				else:
					#append comma with space for displaying proper address
					next_sibling_value = next_sibling_value + ", "
					address = address +  next_sibling_value

		return self.get_string_from_sibling_text(address)

	def registration_details_html_data_parser(self, registration_details_html_data):
		"""
		Table data for RegistrationDetails,
		Parse and set in RegistrationDetails object
		"""
		registration_details_list = []
		registration_details_data = registration_details_html_data.find_all('td', attrs={'colspan':'100'})

		for each_registration_detail_data in registration_details_data:
			registration_type = str(each_registration_detail_data.br.previous_sibling).split(":")[1]
			registration_number = each_registration_detail_data.br.next_sibling
			issue_date = self.get_text_of_next_sibling(registration_number)
			registered_with = str(self.get_text_of_next_sibling(issue_date)).split("With")[1]

			registration_number = str(registration_number).split(":")[1]
			issue_date = str(issue_date).split(":")[1]

			new_registration_details = RegistrationDetails(registration_type= int(registration_type),
				registration_number = self.get_string_from_sibling_text(registration_number), 
				issue_date = self.get_string_from_sibling_text(issue_date), 
				registered_with = self.get_string_from_sibling_text(registered_with))

			registration_details_list.append(new_registration_details)

		return registration_details_list

	
	def rcmc_details_html_data_parser(self, rcmc_details_html_data):
		"""
		Table data for RegistrationCumMembershipCertificateDetails,
		Parse and set in RegistrationCumMembershipCertificateDetails object
		"""
		rcmc_details_list = []
		rcmc_details_data = rcmc_details_html_data.find_all('td', attrs={'colspan':'100'})

		for each_rcmc_detail_data in rcmc_details_data:
			rcmc_id = each_rcmc_detail_data.br.previous_sibling
			rcmc_number = each_rcmc_detail_data.br.next_sibling
			issue_date = self.get_text_of_next_sibling(rcmc_number)
			expiry = self.get_text_of_next_sibling(issue_date)
			issued_by = str(self.get_text_of_next_sibling(expiry)).split(":")[1]

			issue_date = str(issue_date).split(":")[1]
			expiry = str(expiry).split(":")[1]

			new_rcmc_details = RegistrationCumMembershipCertificateDetails(rcmc_id= int(rcmc_id),rcmc_number = self.get_string_from_sibling_text(rcmc_number), 
				issue_date = self.get_string_from_sibling_text(issue_date), expiry = self.get_string_from_sibling_text(expiry),
				issued_by = self.get_string_from_sibling_text(issued_by))

			rcmc_details_list.append(new_rcmc_details)

		return rcmc_details_list


	def get_text_of_next_sibling(self, current_sibling):
		"""
		This helper method returns TEXT of next sibling from current sibling
		"""
		return current_sibling.next_sibling.next_sibling

	def get_string_from_sibling_text(self, sibling_text):
		"""
		This helper method returns string of text removing void spaces
		"""
		return str(sibling_text).strip()

	def save_complete_iec_details(self, importer_exporter_code_details, directors_list, branches_list, registration_details_list, rcmc_details_list):
		"""
		This method associates embedded objects with iec details 
		saves iec details and returns an instance of it
		"""
		importer_exporter_code_details.directors = directors_list
		importer_exporter_code_details.branches = branches_list
		importer_exporter_code_details.registration_details = registration_details_list
		importer_exporter_code_details.rcmc_details = rcmc_details_list

		saved_iec_details = importer_exporter_code_details.save()	

		return saved_iec_details	

	def retrieve_iec_data_with_code(self, importer_exporter_code):
		"""
		This method will searches for a record in DB with IEC code
		which returns a QuerySet 
		if atleast one record is present, return an IEC details object
		"""
		try:
			importer_exporter_code_details = ImporterExporterCodeDetails.objects.get(importer_exporter_code= importer_exporter_code)
			return importer_exporter_code_details
		except ImporterExporterCodeDetails.DoesNotExist:
			raise CustomApiException(utils.IEC_NOT_FOUND_IN_DB, status.HTTP_404_NOT_FOUND)
			














