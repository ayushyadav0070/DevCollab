import threading

_thread_local = threading.local()

def get_current_user():
    return getattr(_thread_local,'user',None)

class CurrentUserMiddleware:
    def __init__(self,get_response):
        self.get_response = get_response
    def __call__(self,request, *args, **kwds):
        _thread_local.user = request.user
        
        try:
            response = self.get_response(request)
        finally:
            if hasattr(_thread_local,'user'):
                del _thread_local.user
        return response
### Celery will create a new thread , which willl ont have access to this
