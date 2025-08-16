# attendance/models.py
import datetime
from django.db import models
from django.utils import timezone

class Attendance(models.Model):
    employee = models.ForeignKey("api.Employee", on_delete=models.CASCADE)
    date = models.DateField()
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('employee', 'date')

    def late_minutes(self):
        """Calculate late arrival in minutes."""
        work_start = timezone.make_aware(
            datetime.datetime.combine(self.date, datetime.time(9, 0))
        )
        if self.check_in and self.check_in > work_start:
            return int((self.check_in - work_start).total_seconds() / 60)
        return 0

    def overtime_minutes(self):
        """Calculate overtime in minutes."""
        work_end = timezone.make_aware(
            datetime.datetime.combine(self.date, datetime.time(17, 0))
        )
        if self.check_out and self.check_out > work_end:
            return int((self.check_out - work_end).total_seconds() / 60)
        return 0

    late_minutes.short_description = "Late Minutes"
    overtime_minutes.short_description = "Overtime Minutes"
