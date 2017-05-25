from django.shortcuts import render
import django_filters
from rest_framework import filters
import json
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.http import HttpResponse
from iec_lookup.services.iec_lookup_service import IECLookupService 
from rest_framework import status
from iec_lookup.serializers import IECDetailsSerializer

@csrf_exempt
def validate_importer_exporter_code(request):
	"""
	request body contains 10 digit code and name of iec
	returns: IEC details of company with all embedded fields
	"""
	try:
		json_body = json.loads(request.body)

		for key, value in json_body.iteritems():
			if value is None or value == "":
				raise ValueError('Please provide '+ key, status.HTTP_400_BAD_REQUEST)

		iec_lookup_service = IECLookupService()
		lookup_validate_iec_response = iec_lookup_service.lookup_validate_iec(json_body)

		serializer = IECDetailsSerializer(lookup_validate_iec_response)
		return JsonResponse(serializer.data, safe=False)
	except ValueError as err:
		HttpResponse.status_code = err.args[1]
		return JsonResponse({'detail': err.args[0]})
	except Exception, e:
		HttpResponse.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
		return JsonResponse({'detail': 'Oops, An Error occured','error': str(e)})


@csrf_exempt
def retrieve_importer_exporter_code(request):
	"""
	request comtains 10 digit code of IEC
	returns: IEC details of company with all embedded fields
	"""
	try:
		code = request.GET.get('code', '')
		if code == "" or code == None :
			raise ValueError('Please provide valid code', status.HTTP_400_BAD_REQUEST)

		iec_lookup_service = IECLookupService()
		iec_data_response = iec_lookup_service.retrieve_iec_data_with_code(code)

		serializer = IECDetailsSerializer(iec_data_response)
		return JsonResponse(serializer.data, safe=False)
	except ValueError as err:
		HttpResponse.status_code = err.args[1]
		return JsonResponse({'detail': err.args[0]})
	except Exception, e:
		HttpResponse.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
		return JsonResponse({'detail': 'Oops, An Error occured','error': str(e)})


