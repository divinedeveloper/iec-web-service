from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException

def iec_custom_exception_handler(exc, context):
    """
    Custom exception handler for Django Rest Framework that adds
    the `status_code` to the response and renames the `detail` key to `error`.
    """
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code
        response.data['error'] = response.data['detail']
        del response.data['detail']

    return response

class CustomApiException(APIException):
    #error fields
    detail = None
    status_code = None

    # create constructor
    def __init__(self, message, status_code):
        #override public fields
        CustomApiException.status_code = status_code
        CustomApiException.detail = message
