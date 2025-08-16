# attendance/signals.py
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from django.conf import settings

from .models import Attendance
from hr.models import PayRoll, CompanyPolicy
from TalentFlow.api.models import Employee  # avoid circular imports

# store (employee_id, year, month) needing recalculation
pending_updates = set()

# Defaults (can be overridden by settings or CompanyPolicy)
DEFAULT_WORK_START = getattr(settings, "ATTENDANCE_WORK_START", "09:00:00")  # "HH:MM:SS"
DEFAULT_WORK_END = getattr(settings, "ATTENDANCE_WORK_END", "17:00:00")
DEFAULT_GRACE_MINUTES = int(getattr(settings, "ATTENDANCE_GRACE_MINUTES", 10))

def parse_time(s):
    return datetime.strptime(s, "%H:%M:%S").time()

WORK_START = parse_time(DEFAULT_WORK_START)
WORK_END = parse_time(DEFAULT_WORK_END)
GRACE = DEFAULT_GRACE_MINUTES


# ---------- STEP 1: Pre-save compute late and overtime ----------
@receiver(pre_save, sender=Attendance)
def compute_attendance_minutes(sender, instance, **kwargs):
    late = 0
    overtime = 0

    if instance.check_in:
        scheduled_dt = datetime.combine(instance.date, WORK_START)
        grace_end = scheduled_dt + timedelta(minutes=GRACE)
        if instance.check_in > grace_end:
            delta = instance.check_in - grace_end
            late = int((delta.total_seconds() + 59) // 60)  # ceil to minutes

    if instance.check_out:
        scheduled_out = datetime.combine(instance.date, WORK_END)
        actual_out = instance.check_out
        if actual_out < scheduled_out:
            actual_out += timedelta(days=1)  # overnight
        if actual_out > scheduled_out:
            delta = actual_out - scheduled_out
            overtime = int((delta.total_seconds() + 59) // 60)

    instance.late_minutes = late
    instance.overtime_minutes = overtime


# ---------- STEP 2: Payroll recalculation logic ----------
def recalc_monthly_payroll(employee, year, month):
    agg = Attendance.objects.filter(
        employee=employee,
        date__year=year,
        date__month=month
    ).aggregate(
        total_late_minutes=Sum('late_minutes'),
        total_overtime_minutes=Sum('overtime_minutes'),
        absent_count=Count('id', filter=Q(status='absent'))
    )

    total_late_minutes = agg.get('total_late_minutes') or 0
    total_overtime_minutes = agg.get('total_overtime_minutes') or 0
    absent_count = agg.get('absent_count') or 0

    late_hours = total_late_minutes / 60
    overtime_hours = total_overtime_minutes / 60

    policy = CompanyPolicy.objects.first()
    late_rate = float(policy.late_deduction_per_hour) if policy else 0.0
    overtime_rate = float(policy.overtime_bonus_per_hour) if policy else 0.0
    absent_amt = float(policy.absent_deduction) if policy else 0.0

    total_deductions = late_hours * late_rate + absent_count * absent_amt
    total_bonus = overtime_hours * overtime_rate

    payroll, _ = PayRoll.objects.get_or_create(
        employee=employee,
        year=year,
        month=month,
        defaults={
            'compensation': employee.salary,
            'bonus': 0,
            'deductions': 0,
            'tax': 0
        }
    )

    payroll.bonus = total_bonus
    payroll.deductions = total_deductions
    payroll.net_pay = payroll.compensation + total_bonus - payroll.tax - total_deductions
    payroll.save()


# ---------- STEP 3: Schedule updates ----------
def schedule_recalculation(employee_id, year, month):
    pending_updates.add((employee_id, year, month))
    transaction.on_commit(run_pending_recalculations)


def run_pending_recalculations():
    global pending_updates
    updates = pending_updates
    pending_updates = set()

    for employee_id, year, month in updates:
        employee = Employee.objects.get(id=employee_id)
        recalc_monthly_payroll(employee, year, month)


# ---------- STEP 4: Trigger updates on save/delete ----------
@receiver(post_save, sender=Attendance)
def attendance_saved(sender, instance, **kwargs):
    schedule_recalculation(instance.employee_id, instance.date.year, instance.date.month)


@receiver(post_delete, sender=Attendance)
def attendance_deleted(sender, instance, **kwargs):
    schedule_recalculation(instance.employee_id, instance.date.year, instance.date.month)
