from rest_framework_mongoengine import serializers
from iec_lookup.models import ImporterExporterCodeDetails


class IECDetailsSerializer(serializers.DocumentSerializer):
	class Meta:
		model = ImporterExporterCodeDetails
		fields = '__all__'