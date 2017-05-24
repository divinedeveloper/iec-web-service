from django.db import models
from datetime import datetime
from mongoengine import Document, EmbeddedDocument, fields
from collections import OrderedDict
import json

# Create your models here.

class Director(EmbeddedDocument):
	"""
	A Director class Document that provides relevant details of director of iec
	It will be embedded in IEC Details Document
	"""
	name = fields.StringField(required=True)
	fathers_name = fields.StringField()
	address = fields.StringField()
	phone_email = fields.StringField()


class Branch(EmbeddedDocument):
	"""
	A Branch class Document that provides relevant details of an iec branch
	It will be embedded in IEC Details Document
	"""
	branch_code = fields.IntField()
	address = fields.StringField()


class RegistrationDetails(EmbeddedDocument):
	"""
	A RegistrationDetails class Document that provides relevant details of an iec registration
	It will be embedded in IEC Details Document
	"""
	registration_type = fields.IntField()
	registration_number = fields.StringField(required=True)
	issue_date = fields.StringField()
	registered_with = fields.StringField()


class RegistrationCumMembershipCertificateDetails(EmbeddedDocument):
	"""
	RegistrationCumMembershipCertificateDetails i.e. RCMC
	A RCMCDetails class Document that provides relevant details of an iec Registration cum Membership Certificate
	It will be embedded in IEC Details Document
	"""
	rcmc_id = fields.IntField()
	rcmc_number = fields.StringField(required=True)
	issue_date = fields.StringField()
	expiry = fields.StringField()
	issued_by = fields.StringField()
	
class ImporterExporterCodeDetails(Document):
	"""
	Importer Exporter Code Details
	An IEC Details class Document that provides relevant details of iec company
	It embeds directors, branches,registration_details and rcmc_details in it
	"""
	importer_exporter_code = fields.StringField(unique=True, required=True)
	importer_exporter_code_allotment_date = fields.StringField()
	file_number = fields.StringField()
	file_date = fields.StringField()
	party_name = fields.StringField(required=True)
	party_address = fields.StringField()
	phone_number = fields.StringField()
	email = fields.StringField()
	exporter_type = fields.StringField(required=True)
	importer_exporter_code_status = fields.StringField(required=True)
	date_of_establishment = fields.StringField()
	bin_pan_extension = fields.StringField()
	pan_issue_date = fields.StringField()
	pan_issued_by = fields.StringField()
	nature_of_concern = fields.StringField(required=True)
	bank_name_and_location = fields.StringField()
	account_type = fields.StringField()
	account_number = fields.StringField()

	#Timestamps
	drip_iec_date_created = fields.DateTimeField(default=lambda: datetime.now())
	drip_iec_last_updated = fields.DateTimeField(default=lambda: datetime.now())
	drip_iec_deleted_at = fields.DateTimeField()

	#activation and deletion flags
	is_active = fields.BooleanField(default=True)
	is_deleted = fields.BooleanField(default=False)

	#Embedded fields
	directors = fields.ListField(fields.EmbeddedDocumentField(Director))
	branches = fields.ListField(fields.EmbeddedDocumentField(Branch))
	registration_details = fields.ListField(fields.EmbeddedDocumentField(RegistrationDetails))
	rcmc_details = fields.ListField(fields.EmbeddedDocumentField(RegistrationCumMembershipCertificateDetails))

class ImporterExporterCodeToBeRetrieved(Document):
	"""
	Importer Exporter Code To be Retrieved
	An ImporterExporterCodeToBeRetrieved Document that provides relevant details of iec company
	whose data needs to be fetched once DGFT site is up
	"""
	importer_exporter_code = fields.StringField(unique=True,required=True)
	name = fields.StringField(required=True)
	is_iec_data_retrieved = fields.BooleanField(default=False)
	
	#Timestamps
	drip_iec_date_created = fields.DateTimeField(default=lambda: datetime.now())
	drip_iec_last_updated = fields.DateTimeField(default=lambda: datetime.now())






