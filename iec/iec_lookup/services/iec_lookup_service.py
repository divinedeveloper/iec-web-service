from django.shortcuts import render
from iec_lookup.models import ImporterExporterCodeDetails, Director, Branch, RegistrationDetails, RegistrationCumMembershipCertificateDetails, ImporterExporterCodeToBeRetrieved
from mongoengine.django.shortcuts import get_document_or_404
from django.conf import settings
from rest_framework import status
from bs4 import BeautifulSoup
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
				self.check_save_iec_to_retrieve(json_body)
				raise ValueError('Sorry, We are facing issues connecting to DGFT site. Please try again later.', status.HTTP_503_SERVICE_UNAVAILABLE)


		return "an object will be returned" 


	def get_iec_with_code_and_name(self, json_body):
		importer_exporter_code_details = ImporterExporterCodeDetails.objects(importer_exporter_code= json_body["code"], party_name_address__istartswith= json_body["name"])
		return importer_exporter_code_details


	def poll_dgft_site_with_iec_and_name(self, json_body):
		dgft_site_response = requests.post(settings.DGFT_SITE_URL, data={'iec': json_body['code'], 'name': json_body['name']})
		# logging.debug(dgft_site_response.text)
		return dgft_site_response.text



	def check_save_iec_to_retrieve(self, json_body):
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
			return
			#parse just the body of html of error message and return message


	def html_to_object_parser_for_success_data(self, dgft_site_response):
		dgft_site_response_soup = BeautifulSoup(dgft_site_response, "html.parser")
		iec_tables = dgft_site_response_soup.findAll("table")
		filled_iec_details_object = self.iec_details_html_data_parser(iec_tables[0])
		filled_directors_list = self.directors_html_data_parser(iec_tables[1])
		# filled_iec_details_object = self.iec_details_html_data_parser(iec_tables[0])
		# filled_iec_details_object = self.iec_details_html_data_parser(iec_tables[0])
		# filled_iec_details_object = self.iec_details_html_data_parser(iec_tables[0])



		# for index, each_iec_table in enumerate(iec_tables):
		# 	if index == 0:
		# 		#it contains iec details data send it to iec html data parser
		# 		logging.debug(each_iec_table)
		# 		logging.debug("###################################################################################")
		# 	if index == 1:
		# 		#it contains Directors data send it to director html data parser
		# 	if index == 2:
		# 		#it contains Branches data send it to Branches html data parser
		# 	if index == 3:
		# 		#it contains Registration Details data send it to Registration Details  html data parser
		# 	if index == 4:
		# 		#it contains RCMC Details  data send it to RCMC html data parser


		# iec_table_data = [[cell.text for cell in row("td") if cell.text != ":"] for row in each_iec_table("tr")]
		# logging.debug(iec_table_data)
		# filtered_iec_table_data =  filter(None, iec_table_data)
		# logging.debug(filtered_iec_table_data)
		
		return #json.dumps(OrderedDict(filtered_iec_table_data))

	def iec_details_html_data_parser(self, iec_html_data):

		iec_table_data_list = [[cell.text for cell in row("td") if cell.text != ":"] for row in iec_html_data("tr")]
		filtered_iec_table_data_list =  filter(None, iec_table_data_list)

		#avoiding duplicates and will get data in order
		ordered_dictionary_of_iec_table_data = OrderedDict(filtered_iec_table_data_list)

		filled_iec_details_object = ImporterExporterCodeDetails(importer_exporter_code = ordered_dictionary_of_iec_table_data['IEC'],
			importer_exporter_code_allotment_date = ordered_dictionary_of_iec_table_data['IEC Allotment Date'], file_number = ordered_dictionary_of_iec_table_data['File Number'],
			file_date = ordered_dictionary_of_iec_table_data['File Date'], party_name_address = ordered_dictionary_of_iec_table_data['Party Name and Address'],
			phone_number = ordered_dictionary_of_iec_table_data['Phone No'], email = ordered_dictionary_of_iec_table_data['e_mail'],
			exporter_type = ordered_dictionary_of_iec_table_data['Exporter Type'], importer_exporter_code_status = ordered_dictionary_of_iec_table_data['IEC Status'],
			date_of_establishment = ordered_dictionary_of_iec_table_data['Date of Establishment'], bin_pan_extension = ordered_dictionary_of_iec_table_data['BIN (PAN+Extension)'],
			pan_issue_date = ordered_dictionary_of_iec_table_data['PAN ISSUE DATE'], pan_issued_by = ordered_dictionary_of_iec_table_data['PAN ISSUED BY'],
			nature_of_concern = ordered_dictionary_of_iec_table_data['Nature Of Concern'], banker_detail = ordered_dictionary_of_iec_table_data['Banker Detail']
			)

		# logging.debug(filled_iec_details_object.party_name_address.strip())

		return filled_iec_details_object

	def directors_html_data_parser(self, directors_html_data):

		logging.debug(directors_html_data)
		#NEDD TO WORK ON THIS LOGIC TO SEPARATE FIELDS BY BR

		directors_table_data_list = [[cell.text for cell in row("td") if cell.text != ":"] for row in directors_html_data("tr")]
		filtered_directors_table_data_list =  filter(None, directors_table_data_list)

		#avoiding duplicates and will get data in order
		ordered_dictionary_of_directors_table_data = OrderedDict(filtered_directors_table_data_list)

		logging.debug(ordered_dictionary_of_directors_table_data)

		return #filled_iec_details_object










