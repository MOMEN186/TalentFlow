# apis/admin.py
from django.contrib import admin
from .models import Employee, Department, JobTitle, LeaveNote,Exit
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "middle_name",
        "last_name",
        "email_display",
        "phone",
        "department",
        "job_title",
    )

    def email_display(self, obj):
        return obj.user.email if obj.user else 'N/A'
    
    email_display.short_description = 'Email' 

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
