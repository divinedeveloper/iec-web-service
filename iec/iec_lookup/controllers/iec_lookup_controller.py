from django.shortcuts import render
import django_filters
from rest_framework import filters
import json
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.http import HttpResponse
from django.http import HttpRequest
from iec_lookup.services.iec_lookup_service import IECLookupService 
from rest_framework import status
from iec_lookup import utils
from iec_lookup.serializers import IECDetailsSerializer
from iec_lookup.custom_exceptions import CustomApiException

@csrf_exempt
def validate_importer_exporter_code(request):
	"""
	request body contains 10 digit code and name of iec
	returns: IEC details of company with all embedded fields
	"""
	try:
		if not request.body:
			raise CustomApiException(utils.REQUEST_BODY_NOT_PROVIDED, status.HTTP_400_BAD_REQUEST )
		
		if not 'application/json' in request.META.get('CONTENT_TYPE'):
			raise CustomApiException(utils.REQUEST_NON_JSON_FORMAT, status.HTTP_400_BAD_REQUEST ) 


		json_body = json.loads(request.body)

		for key, value in json_body.iteritems():
			if value is None or value == "":
				raise CustomApiException(utils.MISSING_FIELD_VALUE+ key, status.HTTP_400_BAD_REQUEST)
			if key == "code" and len(value) != 10:
				raise CustomApiException(utils.INVALID_IEC_CODE, status.HTTP_400_BAD_REQUEST)

		iec_lookup_service = IECLookupService()
		lookup_validate_iec_response = iec_lookup_service.lookup_validate_iec(json_body)

		serializer = IECDetailsSerializer(lookup_validate_iec_response)

		HttpResponse.status_code = status.HTTP_200_OK
		return JsonResponse(serializer.data, safe=False)
	except CustomApiException as err:
		HttpResponse.status_code = err.status_code
		return JsonResponse({'status_code': err.status_code, 'message': err.detail})
	except Exception, e:
		HttpResponse.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
		return JsonResponse({'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR, 'message': str(e)})


@csrf_exempt
def retrieve_importer_exporter_code(request):
	"""
	request comtains 10 digit code of IEC
	returns: IEC details of company with all embedded fields
	"""
	try:
		code = request.GET.get('code', '')
		if code == "" or code == None or len(code) != 10:
			raise CustomApiException(utils.INVALID_IEC_CODE, status.HTTP_400_BAD_REQUEST)

		iec_lookup_service = IECLookupService()
		iec_data_response = iec_lookup_service.retrieve_iec_data_with_code(code)

		serializer = IECDetailsSerializer(iec_data_response)

		HttpResponse.status_code = status.HTTP_200_OK
		return JsonResponse(serializer.data, safe=False)
	except CustomApiException as err:
		HttpResponse.status_code = err.status_code
		return JsonResponse({'status_code': err.status_code, 'message': err.detail})
	except Exception, e:
		HttpResponse.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
		return JsonResponse({'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR, 'message': str(e)})


