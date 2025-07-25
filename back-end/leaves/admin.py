from django.contrib import admin
from .models import LeaveRequest
# Register your models here.

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'employee',
        'leave_type',
        'start_date',
        'end_date',
        'status',
        'approved_by',
        'request_date'
    )
    list_filter = ('status', 'leave_type', 'request_date')
    search_fields = ('employee__user__username', 'reason')