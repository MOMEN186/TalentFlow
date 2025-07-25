from django.contrib import admin
from .models import Department, JobTitle, Employee


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'manager', 'description')
    search_fields = ('name',)


@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'gender',
        'phone',
        'national_id',
        'department',
        'job_title',
        'hire_date',
        'annual_leave_balance',
        'is_active'
    )
    list_filter = ('gender', 'department', 'job_title', 'is_active')
    search_fields = ('first_name', 'last_name', 'phone', 'national_id')
    # list_editable = ('is_active', 'annual_leave_balance', 'job_title', 'department')
    # date_hierarchy = 'hire_date'