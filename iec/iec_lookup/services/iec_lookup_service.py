from django.shortcuts import render
from iec_lookup.models import ImporterExporterCodeDetails, Director, Branch, RegistrationDetails, RegistrationCumMembershipCertificateDetails, ImporterExporterCodeToBeRetrieved
from mongoengine.django.shortcuts import get_document_or_404
from django.conf import settings
from rest_framework import status
from bs4 import BeautifulSoup, NavigableString, Tag
from collections import OrderedDict
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
		checks if code and name exists in our db
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
			#return as JSON
			return importer_exporter_code_details
		else:
			try:
				dgft_site_response = self.poll_dgft_site_with_iec_and_name(json_body)

				return self.handle_dgft_response(dgft_site_response)
				
			except requests.exceptions.RequestException as e:
				#check if it exists in retrieval document, if not create one 
				self.get_or_save_iec_to_retrieve_data(json_body)
				raise ValueError('Sorry, We are facing issues connecting to DGFT site. Please try again later.', status.HTTP_503_SERVICE_UNAVAILABLE)


		return "an object will be returned" 


	def get_iec_with_code_and_name(self, json_body):
		importer_exporter_code_details = ImporterExporterCodeDetails.objects(importer_exporter_code= json_body["code"], party_name_address__istartswith= json_body["name"])
		return importer_exporter_code_details


	def poll_dgft_site_with_iec_and_name(self, json_body):
		dgft_site_response = requests.post(settings.DGFT_SITE_URL, data={'iec': json_body['code'], 'name': json_body['name']})
		# logging.debug(dgft_site_response.text)
		return dgft_site_response.text



	def get_or_save_iec_to_retrieve_data(self, json_body):
		importer_exporter_code_to_retrieve = ImporterExporterCodeToBeRetrieved.objects(importer_exporter_code= json_body["code"], name__istartswith= json_body["name"])
		if importer_exporter_code_to_retrieve:
			return
		else:
			ImporterExporterCodeToBeRetrieved(importer_exporter_code= json_body["code"], name= json_body['name']).save()
			return

	def handle_dgft_response(self, dgft_site_response):
		#if invalid response throw exceptions with corresponding messages
		#else send to parse html

		if dgft_site_response == settings.DGFT_IEC_NOT_PROPER_ERROR:
			raise ValueError('Please enter proper iec code', status.HTTP_400_BAD_REQUEST)
		if dgft_site_response == settings.DGFT_APPLICANT_NAME_NOT_PROPER_ERROR:
			raise ValueError('Please enter proper iec name', status.HTTP_400_BAD_REQUEST)
		if settings.DGFT_SUCCESS_REPLY in dgft_site_response:
			#parse html and convert to json or dict and save in db
			return self.html_to_object_parser_for_success_data(dgft_site_response)
		else:
			#parse just the body of html of error message and throw exception message
			return self.html_to_object_parser_for_error_data(dgft_site_response)
			


	def html_to_object_parser_for_success_data(self, dgft_site_response):
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
		dgft_site_error_response_soup = BeautifulSoup(dgft_site_error_response, "html.parser")
		dgft_site_error_message = str(dgft_site_error_response_soup.find("body").text)

		raise ValueError(dgft_site_error_message, status.HTTP_400_BAD_REQUEST)


	def iec_details_html_data_parser(self, iec_html_data):

		iec_table_data_list = [[cell.text for cell in row("td") if cell.text != ":"] for row in iec_html_data("tr")]
		filtered_iec_table_data_list =  filter(None, iec_table_data_list)

		#avoiding duplicates and will get data in order
		ordered_dictionary_of_iec_table_data = OrderedDict(filtered_iec_table_data_list)

		importer_exporter_code_details = ImporterExporterCodeDetails(importer_exporter_code = ordered_dictionary_of_iec_table_data['IEC'],
			importer_exporter_code_allotment_date = ordered_dictionary_of_iec_table_data['IEC Allotment Date'], file_number = ordered_dictionary_of_iec_table_data['File Number'],
			file_date = ordered_dictionary_of_iec_table_data['File Date'], party_name_address = ordered_dictionary_of_iec_table_data['Party Name and Address'],
			phone_number = ordered_dictionary_of_iec_table_data['Phone No'], email = ordered_dictionary_of_iec_table_data['e_mail'],
			exporter_type = ordered_dictionary_of_iec_table_data['Exporter Type'], importer_exporter_code_status = ordered_dictionary_of_iec_table_data['IEC Status'],
			date_of_establishment = ordered_dictionary_of_iec_table_data['Date of Establishment'], bin_pan_extension = ordered_dictionary_of_iec_table_data['BIN (PAN+Extension)'],
			pan_issue_date = ordered_dictionary_of_iec_table_data['PAN ISSUE DATE'], pan_issued_by = ordered_dictionary_of_iec_table_data['PAN ISSUED BY'],
			nature_of_concern = ordered_dictionary_of_iec_table_data['Nature Of Concern'], banker_detail = ordered_dictionary_of_iec_table_data['Banker Detail']
			)

		return importer_exporter_code_details

	def directors_html_data_parser(self, directors_html_data):
		directors_list = []
		directors_data = directors_html_data.find_all('td', attrs={'colspan':'100'})
		for each_director_data in directors_data:
			director_name = each_director_data.br.previous_sibling
			fathers_name = each_director_data.br.next_sibling
			address_line_1 = self.get_text_of_next_sibling(fathers_name) 
			address_line_2 = self.get_text_of_next_sibling(address_line_1)
			address_line_3 = self.get_text_of_next_sibling(address_line_2)
			address_line_4 = self.get_text_of_next_sibling(address_line_3)
			phone_email = self.get_text_of_next_sibling(address_line_4)

			new_director = Director(name= self.get_string_from_sibling_text(director_name), fathers_name= self.get_string_from_sibling_text(fathers_name),
				address_line_1 = self.get_string_from_sibling_text(address_line_1), address_line_2 = self.get_string_from_sibling_text(address_line_2),
				address_line_3 = self.get_string_from_sibling_text(address_line_3), address_line_4 = self.get_string_from_sibling_text(address_line_4),
				phone_email = self.get_string_from_sibling_text(phone_email))

			directors_list.append(new_director) 
		return directors_list

	def branches_html_data_parser(self, branches_html_data):
		branches_list = []
		branches_data = branches_html_data.find_all('td', attrs={'colspan':'100'})
		for each_branch_data in branches_data:
			branch_code = str(each_branch_data.br.previous_sibling).split(":")[1]
			address_line_1 = each_branch_data.br.next_sibling
			address_line_2 = self.get_text_of_next_sibling(address_line_1)
			address_line_3 = self.get_text_of_next_sibling(address_line_2)
			address_line_4 = self.get_text_of_next_sibling(address_line_3)

			new_branch = Branch(branch_code= int(branch_code),address_line_1 = self.get_string_from_sibling_text(address_line_1), 
				address_line_2 = self.get_string_from_sibling_text(address_line_2), address_line_3 = self.get_string_from_sibling_text(address_line_3), 
				address_line_4 = self.get_string_from_sibling_text(address_line_4))

			branches_list.append(new_branch)

		return branches_list
		
	def registration_details_html_data_parser(self, registration_details_html_data):
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
		return current_sibling.next_sibling.next_sibling

	def get_string_from_sibling_text(self, sibling_text):
		return str(sibling_text)

	def save_complete_iec_details(self, importer_exporter_code_details, directors_list, branches_list, registration_details_list, rcmc_details_list):
		importer_exporter_code_details.directors = directors_list
		importer_exporter_code_details.branches = branches_list
		importer_exporter_code_details.registration_details = registration_details_list
		importer_exporter_code_details.rcmc_details = rcmc_details_list

		saved_iec_details = importer_exporter_code_details.save()	
		return saved_iec_details	














