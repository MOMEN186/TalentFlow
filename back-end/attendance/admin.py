# attendance/admin.py
from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in', 'check_out', 'late_minutes', 'overtime_minutes')
    list_filter = ('date', 'employee')
    search_fields = ('employee__first_name', 'employee__last_name')
