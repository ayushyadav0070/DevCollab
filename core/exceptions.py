from rest_framework.views import exception_handler
from rest_framework.response import Response

def devcollab_exception_handler(excep,context):
    response = exception_handler(excep,context)
    if response is not None:
        response.data = {
            'error':True,
            'code':response.status_code,
            'detail':response.data
        }
    return response