# api/reports/views.py
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from TalentFlow.accounts.permissions import IsHRUser
from TalentFlow.api.models import Employee, Exit
from .utils import parse_date, active_filter_for_date, find_first_field


def _month_iso_from_trunc_value(m):
    """
    Normalize value returned by TruncMonth to an ISO date string.
    Works whether m is a datetime, date, or string.
    """
    if m is None:
        return None
    # datetime-like (has .date)
    if hasattr(m, "date") and not isinstance(m, str):
        try:
            return m.date().isoformat()
        except Exception:
            return m.isoformat()
    # date-like
    try:
        return m.isoformat()
    except Exception:
        return str(m)


class ReportsTurnoverAPIView(APIView):
    permission_classes = [IsAuthenticated, IsHRUser]
    """
    GET /api/reports/turnover/?start=YYYY-MM-DD&end=YYYY-MM-DD
    Returns hires, exits, monthly series, and attrition rate for the period.
    """
    def get(self, request):
        # parse dates (default last 30 days)
        end = parse_date(request.GET.get("end")) or timezone.localdate()
        start = parse_date(request.GET.get("start")) or (end - timedelta(days=30))
        if start > end:
            start, end = end, start

        # detect hire field on Employee (date_joined is present in your model)
        hire_field = find_first_field(Employee, ['hire_date', 'date_joined', 'joined_date'])

        # HIRES in period
        if hire_field:
            hires_qs = Employee.objects.filter(**{f"{hire_field}__gte": start, f"{hire_field}__lte": end})
        else:
            hires_qs = Employee.objects.none()
        hires_total = hires_qs.count()

        # HIRES by month
        hires_by_month = []
        if hire_field:
            hits = hires_qs.annotate(month=TruncMonth(hire_field)).values('month').annotate(count=Count('id')).order_by('month')
            for item in hits:
                month_iso = _month_iso_from_trunc_value(item.get('month'))
                hires_by_month.append({"month": month_iso, "count": item.get('count', 0)})

        # EXITS in period
        # Prefer Exit model as source-of-truth. If there are no Exit rows in period, fall back to Employee.termination_date
        exits_qs = Exit.objects.filter(exit_date__gte=start, exit_date__lte=end)
        exits_total = exits_qs.count()

        # fallback: if no Exit rows were found and Employee has termination_date usage, derive from Employee
        if exits_total == 0:
            term_field = find_first_field(Employee, ['termination_date', 'termintion_date', 'left_date', 'exit_date'])
            if term_field:
                exits_qs = Employee.objects.filter(**{f"{term_field}__gte": start, f"{term_field}__lte": end})
                exits_total = exits_qs.count()
                # mark that this queryset is from Employee (not Exit) for later TruncMonth usage
                exits_from_employee = True
            else:
                exits_qs = Employee.objects.none()
                exits_from_employee = False
        else:
            exits_from_employee = False  # we used Exit model

        # EXITS by month
        exits_by_month = []
        if exits_qs.exists():
            # choose correct trunc field name depending on whether we have Exit or Employee queryset
            trunc_field = 'exit_date' if not exits_from_employee else find_first_field(Employee, ['termination_date', 'termintion_date', 'left_date', 'exit_date'])
            # annotate & group
            exs = exits_qs.annotate(month=TruncMonth(trunc_field)).values('month').annotate(count=Count('id')).order_by('month')
            for item in exs:
                month_iso = _month_iso_from_trunc_value(item.get('month'))
                exits_by_month.append({"month": month_iso, "count": item.get('count', 0)})

        # headcount at start and end using active_filter_for_date (uses date_joined/termination_date)
        hc_start = Employee.objects.filter(active_filter_for_date(Employee, start)).count()
        hc_end = Employee.objects.filter(active_filter_for_date(Employee, end)).count()

        # average headcount and attrition
        avg_headcount = (hc_start + hc_end) / 2 if (hc_start + hc_end) > 0 else max(hc_start, hc_end, 1)
        attrition_rate = (exits_total / avg_headcount) * 100 if avg_headcount else 0

        result = {
            "date_range": {"start": start.isoformat(), "end": end.isoformat()},
            "hires_total": hires_total,
            "exits_total": exits_total,
            "hires_by_month": hires_by_month,
            "exits_by_month": exits_by_month,
            "headcount_start": hc_start,
            "headcount_end": hc_end,
            "avg_headcount": round(avg_headcount, 2),
            "attrition_rate_percent": round(attrition_rate, 4)
        }
        return Response(result, status=status.HTTP_200_OK)
