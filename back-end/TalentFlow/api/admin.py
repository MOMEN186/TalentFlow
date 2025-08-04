# apis/admin.py
from django.contrib import admin
from .models import Employee, Department, JobTitle, LeaveNote, PayRoll

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "middle_name",
        "last_name",
        "email",
        "phone",
        "department",
        "job_title",
    )

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(LeaveNote)
class LeaveNoteAdmin(admin.ModelAdmin):
    list_display = ('name', 'employee', 'date', 'return_date')

@admin.register(PayRoll)
class PayRollAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'net_pay', 'gross_pay')
