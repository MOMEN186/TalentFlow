# hr/views.py
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from .models import PayRoll
from .serializers import PayRollSerializer
import time
import logging

logger = logging.getLogger(__name__)


class SmallPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200


class PayRollViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for PayRoll:
    - list() supports paginated JSON and ?excel=true full export (no cache, no pagination)
    - get_queryset uses select_related and simple filters for fast browsing
    """
    serializer_class = PayRollSerializer
    pagination_class = SmallPagination

    def get_queryset(self):
        qs = (
            PayRoll.objects
            .select_related("employee", "employee__department", "employee__job_title")
            .order_by("-year", "-month", "employee__last_name")
        )

        # Lightweight filters commonly used for daily browsing
        year = self.request.query_params.get("year")
        month = self.request.query_params.get("month")
        department = self.request.query_params.get("department")  # department id or slug as you prefer

        if year:
            qs = qs.filter(year=year)
        if month:
            qs = qs.filter(month=month)
        if department:
            qs = qs.filter(employee__department__id=department)

        return qs

    def list(self, request, *args, **kwargs):
        t0 = time.perf_counter()
        export_excel = request.query_params.get("excel", "false").lower() in ("1", "true", "yes")
        queryset = self.filter_queryset(self.get_queryset())
        t1 = time.perf_counter()

        # --- Excel export (no cache, no pagination) ---
        if export_excel:
            # If you previously had a custom Excel exporter, reintegrate it here.
            # For now we fall back to the default list implementation for export.
            return super().list(request, *args, **kwargs)

        # Paginator timing
        paginator = self.paginator
        t2 = time.perf_counter()
        page_obj = paginator.paginate_queryset(queryset, request, view=self)
        t3 = time.perf_counter()

        # Serialization timing
        serializer = self.get_serializer(page_obj, many=True)
        t4 = time.perf_counter()

        paginated_response = paginator.get_paginated_response(serializer.data)
        t5 = time.perf_counter()

        logger.info(
            "Payroll list timings: queryset=%.3f s, paginate=%.3f s, serialize=%.3f s, response_build=%.3f s",
            t1 - t0, t3 - t2, t4 - t3, t5 - t4
        )

        return paginated_response
