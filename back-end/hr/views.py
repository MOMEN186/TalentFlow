# hr/views.py
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from .models import PayRoll
from .serializers import PayRollSerializer, PayRollCreateUpdateSerializer
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
    # ✅ استخدم الـ Serializer الخاص بالقراءة كافتراضي
    serializer_class = PayRollSerializer
    pagination_class = SmallPagination

    # ✅ قم بتحديد الـ Serializer الذي سيتم استخدامه لكل عملية
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PayRollCreateUpdateSerializer
        return PayRollSerializer

    def get_queryset(self):
        qs = (
            PayRoll.objects
            .select_related("employee", "employee__department", "employee__job_title")
            .order_by("-year", "-month", "employee__last_name")
        )

        year = self.request.query_params.get("year")
        month = self.request.query_params.get("month")
        department = self.request.query_params.get("department")

        if year:
            qs = qs.filter(year=year)
        if month:
            qs = qs.filter(month=month)
        if department:
            qs = qs.filter(employee__department__id=department)

        return qs

    def list(self, request, *args, **kwargs):
        # الكود الخاص بـ list() كما هو
        t0 = time.perf_counter()
        export_excel = request.query_params.get("excel", "false").lower() in ("1", "true", "yes")
        queryset = self.filter_queryset(self.get_queryset())
        t1 = time.perf_counter()

        if export_excel:
            return super().list(request, *args, **kwargs)

        paginator = self.paginator
        t2 = time.perf_counter()
        page_obj = paginator.paginate_queryset(queryset, request, view=self)
        t3 = time.perf_counter()

        serializer = self.get_serializer(page_obj, many=True)
        t4 = time.perf_counter()

        paginated_response = paginator.get_paginated_response(serializer.data)
        t5 = time.perf_counter()

        logger.info(
            "Payroll list timings: queryset=%.3f s, paginate=%.3f s, serialize=%.3f s, response_build=%.3f s",
            t1 - t0, t3 - t2, t4 - t3, t5 - t4
        )

        return paginated_response
