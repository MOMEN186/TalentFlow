
# ==============================================
# reports/services.py
# ==============================================
from typing import Dict, Optional
from django.db.models import Count, Sum, F, Value, Q
from django.db.models.functions import Coalesce, TruncDate, TruncMonth, TruncYear
from django.core.exceptions import FieldError
from .utils import apply_range

# Import your domain models (adjust import paths to your project structure)
from attendance.models import Attendance
from TalentFlow.api.models import Department, Employee, LeaveNote
from hr.models import PayRoll


# ---- Helpers ---------------------------------------------------------------

def _safe_filter_present(qs):
    """Try to approximate 'present' rows without assuming a specific field schema."""
    # Heuristics: status == 'present' OR has a non-null check_in OR marked present flag
    q = Q()
    try:
        q |= Q(status__iexact="present")
    except Exception:
        pass
    try:
        q |= Q(check_in__isnull=False)
    except Exception:
        pass
    try:
        q |= Q(is_present=True)
    except Exception:
        pass
    return qs.filter(q) if q.children else qs


def _try_agg(qs, **aggregates) -> Dict:
    """Run aggregates safely; drop ones that error due to missing fields."""
    out = {}
    for key, agg in aggregates.items():
        try:
            out[key] = qs.aggregate(**{key: agg})[key]
        except FieldError:
            # silently skip if field doesn't exist
            out[key] = None
    return out


def _payroll_amount_expr():
    """Attempt to compute payable amount regardless of exact field naming.
    Tries amount -> net_salary -> gross -> total.
    """
    return Coalesce(F("amount"), Coalesce(F("net_salary"), Coalesce(F("gross"), F("total"))), Value(0))


# ---- Attendance Reports ----------------------------------------------------

def employee_attendance(employee_id: int, start=None, end=None):
    qs = Attendance.objects.filter(employee_id=employee_id)
    # try common datetime field names
    for field in ("date", "created_at", "day", "check_in"):
        if field in [f.name for f in Attendance._meta.get_fields() if hasattr(f, "attname")]:
            qs = apply_range(qs, field, start, end)
            break

    present_qs = _safe_filter_present(qs)

    # group by date for a trend
    try:
        series = (
            present_qs.annotate(day=TruncDate("check_in"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
    except FieldError:
        # fallback to created_at/date if check_in absent
        fallback_field = "date" if hasattr(Attendance, "date") else "id"
        series = (
            present_qs.annotate(day=TruncDate(fallback_field))
            .values("day").annotate(count=Count("id")).order_by("day")
        )

    sums = _try_agg(
        qs,
        total_records=Count("id"),
    )

    return {
        "employee_id": employee_id,
        "total_records": sums.get("total_records", 0) or 0,
        "present_days": series,  # list of {day, count}
    }


def department_attendance(department_id: int, start=None, end=None):
    qs = Attendance.objects.filter(employee__department_id=department_id)
    # date range similar to above
    for field in ("date", "created_at", "day", "check_in"):
        if field in [f.name for f in Attendance._meta.get_fields() if hasattr(f, "attname")]:
            qs = apply_range(qs, field, start, end)
            break

    present_qs = _safe_filter_present(qs)

    # Group by date
    try:
        series = (
            present_qs.annotate(day=TruncDate("check_in"))
            .values("day").annotate(count=Count("id")).order_by("day")
        )
    except FieldError:
        series = (
            present_qs.annotate(day=TruncDate("id"))  # harmless fallback
            .values("day").annotate(count=Count("id")).order_by("day")
        )

    # Headcount in dept
    employee_count = Employee.objects.filter(department_id=department_id).count()

    return {
        "department_id": department_id,
        "employee_count": employee_count,
        "attendance_series": series,
    }


# ---- Department Summary ----------------------------------------------------

def department_summary(department_id: int, start=None, end=None):
    # Employee headcount
    employees = Employee.objects.filter(department_id=department_id)
    headcount = employees.count()

    # Payroll total (date range by typical fields: month/year or created_at)
    prs = PayRoll.objects.filter(employee__department_id=department_id)

    # Apply range if payroll has date/datetime field
    for field in ("date", "created_at", "pay_date"):
        if field in [f.name for f in PayRoll._meta.get_fields() if hasattr(f, "attname")]:
            prs = apply_range(prs, field, start, end)
            break

    total_pay = prs.aggregate(total=Sum(_payroll_amount_expr()))["total"] or 0

    return {
        "department_id": department_id,
        "headcount": headcount,
        "payroll_total": total_pay,
    }


# ---- Payroll Summary -------------------------------------------------------

def payroll_summary(group_by: str = "month", start=None, end=None):
    qs = PayRoll.objects.all()

    # date-like selection
    date_field = None
    for f in ("date", "created_at", "pay_date"):
        if f in [x.name for x in PayRoll._meta.get_fields() if hasattr(x, "attname")]:
            date_field = f
            break

    if date_field:
        qs = apply_range(qs, date_field, start, end)
        if group_by == "year":
            qs = qs.annotate(period=TruncYear(date_field))
        elif group_by == "day":
            qs = qs.annotate(period=TruncDate(date_field))
        else:
            qs = qs.annotate(period=TruncMonth(date_field))
        data = (
            qs.values("period")
            .annotate(total=Sum(_payroll_amount_expr()), count=Count("id"))
            .order_by("period")
        )
    else:
        data = qs.annotate(period=Value("all")).values("period").annotate(total=Sum(_payroll_amount_expr()), count=Count("id"))

    return {"group_by": group_by, "series": data}


# ---- Leave Report ----------------------------------------------------------

def leave_summary(employee_id: Optional[int] = None, start=None, end=None):
    qs = LeaveNote.objects.all()

    # guess date field
    for field in ("start_date", "created_at", "date"):
        if field in [f.name for f in LeaveNote._meta.get_fields() if hasattr(f, "attname")]:
            qs = apply_range(qs, field, start, end)
            break

    if employee_id:
        qs = qs.filter(employee_id=employee_id)

    # group by type if exists
    try:
        breakdown = qs.values("leave_type").annotate(total=Count("id")).order_by("leave_type")
    except FieldError:
        breakdown = qs.annotate(leave_type=Value("unknown")).values("leave_type").annotate(total=Count("id"))

    return {
        "employee_id": employee_id,
        "total": sum(row["total"] for row in breakdown) if breakdown else 0,
        "breakdown": breakdown,
    }


# ---- Organization Overview -------------------------------------------------

def organization_overview(start=None, end=None):
    # Employees & Departments
    dept_count = Department.objects.count()
    emp_count = Employee.objects.count()

    # Attendance (present records in range)
    att_qs = Attendance.objects.all()
    for field in ("date", "created_at", "check_in"):
        if field in [f.name for f in Attendance._meta.get_fields() if hasattr(f, "attname")]:
            att_qs = apply_range(att_qs, field, start, end)
            break
    present_count = _safe_filter_present(att_qs).count()

    # Payroll total in range
    pr_qs = PayRoll.objects.all()
    for field in ("date", "created_at", "pay_date"):
        if field in [f.name for f in PayRoll._meta.get_fields() if hasattr(f, "attname")]:
            pr_qs = apply_range(pr_qs, field, start, end)
            break
    payroll_total = pr_qs.aggregate(total=Sum(_payroll_amount_expr()))["total"] or 0

    # Leaves total in range
    lv_qs = LeaveNote.objects.all()
    for field in ("start_date", "created_at", "date"):
        if field in [f.name for f in LeaveNote._meta.get_fields() if hasattr(f, "attname")]:
            lv_qs = apply_range(lv_qs, field, start, end)
            break
    leaves_total = lv_qs.count()

    return {
        "departments": dept_count,
        "employees": emp_count,
        "attendance_present_records": present_count,
        "payroll_total": payroll_total,
        "leaves_total": leaves_total,
    }

