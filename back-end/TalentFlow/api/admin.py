# apis/admin.py
from django.contrib import admin
from .models import Employee, Department, JobTitle, LeaveNote,Exit
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


@admin.register(Exit)
class ExitAdmin(admin.ModelAdmin):
    list_display = ('employee', 'exit_date', 'reason',"notes","exit_type","recorded_by","final_settlement_amount")
