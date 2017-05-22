from rest_framework_mongoengine import serializers
from iec_lookup.models import ImporterExporterCodeDetails


class IECDetailsSerializer(serializers.DocumentSerializer):
	class Meta:
		model = ImporterExporterCodeDetails
		fields = ('id', 'importer_exporter_code', 'directors', 'branches', 'registration_details', 'rcmc_details')
		# fields = '__all__'