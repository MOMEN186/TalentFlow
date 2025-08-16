#hr/admin.py
from django.contrib import admin
from .models import PayRoll, CompanyPolicy

@admin.register(PayRoll)
class PayRollAdmin(admin.ModelAdmin):
    list_display = ('employee', 'year', 'month', 'gross_pay', 'net_pay', 'bonus', 'deductions', 'tax')
    list_filter = ('year', 'month')
    search_fields = ('employee__first_name', 'employee__last_name')

@admin.register(CompanyPolicy)
class CompanyPolicyAdmin(admin.ModelAdmin):
    list_display = ('late_deduction_per_hour', 'overtime_bonus_per_hour', 'absent_deduction')
    