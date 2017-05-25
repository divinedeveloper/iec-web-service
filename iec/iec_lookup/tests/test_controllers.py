# from django.test import TestCase
from rest_framework.test import APIClient
import pytest

# Create your tests here.

# Feature: To be able to do something
#   In order to do something
#   As someone
#   I want the system to do this thing

# Scenario: A sample one
#   Given this situation
#   When I do something
#   Then what I get is what I was expecting for

class TestValidateImporterExporterCode:

	def setup_method(self):
		"""
		Get instance of API client
		"""
		self.client = APIClient()

	def test_validate_importer_exporter_code(self):
		"""
		first close connection for main db before connecting to test db
		warning: If this not done, maindb will be erased completely for each test
		"""
		#uese rest cleint
		response = self.client.get(reverse('lookup/'))
       	self.assertEqual(response.status_code, status.HTTP_200_OK)

	# def teardown_method(self):
	# 	"""
	# 	Close the local database connection
	# 	if open due to errors or non execution of test_disconnecting_main_db()
	# 	"""
	# 	self.main_db.close()
