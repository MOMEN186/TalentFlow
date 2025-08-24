# middleware/profiling.py
import time
import logging

logger = logging.getLogger(__name__)

class MiddlewareProfiler:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()
        response = self.get_response(request)
        duration = (time.perf_counter() - start) * 1000
        logger.info(f"Request took {duration:.2f} ms")
        return response
