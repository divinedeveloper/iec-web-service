from rest_framework_mongoengine import serializers
from iec_lookup.models import ImporterExporterCodeDetails, Director


class IECDetailsSerializer(serializers.DocumentSerializer):
	"""
	Document serializer for ImporterExporterCodeDetails Model
	with depth automatically serializes all fields in all Embedded documents to. 
	"""
	class Meta:
		model = ImporterExporterCodeDetails
		depth = 2
