# middlewares/performance.py
import time
import uuid
import logging
import traceback
from django.conf import settings

logger = logging.getLogger("performance")

# Threshold in seconds to mark a request as slow
SLOW_REQUEST_THRESHOLD = getattr(settings, "SLOW_REQUEST_THRESHOLD", 0.10)

class PerformanceMiddleware:
    """
    Modern, simple middleware that works for sync and async Django.
    Logs: method, full path (incl. querystring), status_code, duration, user_id (if any),
    response size (if available), and a generated request_id which is added as X-Request-ID.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def _build_path(self, request):
        qs = request.META.get("QUERY_STRING", "")
        if qs:
            return f"{request.path}?{qs}"
        return request.path

    def _log(self, level, msg, **kwargs):
        # Simple structured-ish message — adjust to your logging/JSON-formatter if you have one
        parts = [f"{k}={v}" for k, v in kwargs.items()]
        logger.log(level, "%s | %s", msg, " ".join(parts))

    def __call__(self, request):
        request_id = str(uuid.uuid4())
        request._perf_request_id = request_id
        # expose request id to downstream (views / templates)
        # also return in response headers below
        start = time.perf_counter()
        try:
            response = self.get_response(request)
        except Exception as exc:
            duration = time.perf_counter() - start
            # log exception with traceback
            tb = traceback.format_exc()
            self._log(
                logging.ERROR,
                "EXCEPTION in request",
                request_id=request_id,
                method=request.method,
                path=self._build_path(request),
                user=(getattr(request, "user", None).id if getattr(request, "user", None) and request.user.is_authenticated else "anon"),
                duration=f"{duration:.3f}s",
                exc=str(exc),
                traceback=tb.replace("\n", " | ")
            )
            raise

        duration = time.perf_counter() - start
        status = getattr(response, "status_code", "n/a")
        # response content length — some platforms expose it, otherwise try len(content)
        content_length = response.get("Content-Length") if hasattr(response, "get") else None
        if content_length is None:
            try:
                content_length = len(response.content)
            except Exception:
                content_length = "n/a"

        meta = {
            "request_id": request_id,
            "method": request.method,
            "path": self._build_path(request),
            "status": status,
            "duration_s": f"{duration:.3f}",
            "user": (getattr(request, "user", None).id if getattr(request, "user", None) and request.user.is_authenticated else "anon"),
            "size": content_length,
        }

        # Info log for all requests
        self._log(logging.INFO, "REQ", **meta)

        # Warning for slow requests
        if duration > SLOW_REQUEST_THRESHOLD:
            self._log(logging.WARNING, "SLOW REQUEST", **meta)

        # add request id header so traces can be correlated
        try:
            response["X-Request-ID"] = request_id
        except Exception:
            pass

        return response
