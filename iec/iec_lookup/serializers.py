from rest_framework_mongoengine import serializers
from iec_lookup.models import ImporterExporterCodeDetails, Director, Branch, RegistrationDetails,RegistrationCumMembershipCertificateDetails

class IECDetailsSerializer(serializers.DocumentSerializer):
	"""
	Document serializer for ImporterExporterCodeDetails
	depth field automatically serializes all fields in all Embedded documents to. 
	"""
	class Meta:
		model = ImporterExporterCodeDetails
		fields = '__all__'
		depth = 3
