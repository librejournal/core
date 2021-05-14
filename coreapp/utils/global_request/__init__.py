import threading

from django.utils.deprecation import MiddlewareMixin

_thread_locals = threading.local()


def get_current_request():
    return getattr(_thread_locals, "request", None)


def set_current_request(request):
    setattr(_thread_locals, "request", request)


def reset_current_request():
    setattr(_thread_locals, "request", None)


class RequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        set_current_request(request)

    def process_response(self, request, response):
        reset_current_request()
        return response
