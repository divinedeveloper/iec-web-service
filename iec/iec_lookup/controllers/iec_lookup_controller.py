from django.shortcuts import render
import django_filters
from rest_framework import filters
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from iec_lookup.services.iec_lookup_service import IECLookupService 
from rest_framework import status
from rest_framework.decorators import api_view
from iec_lookup.serializers import IECDetailsSerializer

@csrf_exempt
# @api_view(['GET', 'POST'])
def validate_importer_exporter_code(request):
	"""
	request body contains code and name
	"""
	# try:
	json_body = json.loads(request.body)

	for key, value in json_body.iteritems():
		if value is None or value == "" or value == 0 :
			raise ValueError('Please provide '+ key, status.HTTP_400_BAD_REQUEST)

	iec_lookup_service = IECLookupService()
	lookup_validate_iec_response = iec_lookup_service.lookup_validate_iec(json_body)

	# #trying seralizers lets see if it works
	# lookup_field = 'id'
	# serializer_class = IECDetailsSerializer


	serializer = IECDetailsSerializer(lookup_validate_iec_response, many=True)
	return JsonResponse(serializer.data, safe=False)


	# HttpResponse.status_code = status.HTTP_201_CREATED
	# return JsonResponse({"resp": lookup_validate_iec_response});
	# except ValueError as err:
	# 	HttpResponse.status_code = err.args[1]
	# 	return JsonResponse({'detail': err.args[0], 'status' : err.args[1]})
	# except Exception, e:
	# 	HttpResponse.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
	# 	return JsonResponse({'detail': 'Oops, An Error occured','error': str(e), 'status':status.HTTP_500_INTERNAL_SERVER_ERROR})


def retrieve_importer_exporter_code(request):
	try:
		code = request.GET.get('code', '')
		if code == "" or code == None :
			raise ValueError('Please provide flat type', status.HTTP_400_BAD_REQUEST)

		iec_lookup_service = IECLookupService()
		iec_data_response = iec_lookup_service.retrieve_iec_data_with_code(code)

		serializer = IECDetailsSerializer(iec_data_response, many=True)
		return JsonResponse(serializer.data, safe=False)


	# HttpResponse.status_code = status.HTTP_201_CREATED
	# return JsonResponse({"resp": lookup_validate_iec_response});
	except ValueError as err:
		HttpResponse.status_code = err.args[1]
		return JsonResponse({'detail': err.args[0], 'status' : err.args[1]})
	except Exception, e:
		HttpResponse.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
		return JsonResponse({'detail': 'Oops, An Error occured','error': str(e), 'status':status.HTTP_500_INTERNAL_SERVER_ERROR})


