import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger("performance")

class PerformanceMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, "_start_time"):
            duration = time.time() - request._start_time
            logger.info(f"{request.method} {request.path} took {duration:.2f}s")
            if duration > 1.0:  # log slow requests separately
                logger.warning(f"SLOW REQUEST: {request.method} {request.path} took {duration:.2f}s")
        return response
