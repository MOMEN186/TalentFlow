from rest_framework import serializers
from .models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    # Employee name fields
    first_name = serializers.SerializerMethodField()
    middle_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()

    # Employee department and job title
    department = serializers.SerializerMethodField()
    job_title = serializers.SerializerMethodField()

    # Computed fields
    late_minutes = serializers.SerializerMethodField()
    overtime_minutes = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            "id",
            "employee",     # employee ID for POST/PUT
            "first_name",
            "middle_name",
            "last_name",
            "department",
            "job_title",
            "date",
            "check_in",
            "check_out",
            "late_minutes",
            "overtime_minutes",
        ]

    # Employee name methods
    def get_first_name(self, obj):
        return obj.employee.first_name if obj.employee else None

    def get_middle_name(self, obj):
        return obj.employee.middle_name if obj.employee else None

    def get_last_name(self, obj):
        return obj.employee.last_name if obj.employee else None

    # Department and Job Title methods
    def get_department(self, obj):
        return obj.employee.department.name if obj.employee and obj.employee.department else None

    def get_job_title(self, obj):
        return obj.employee.job_title.name if obj.employee and obj.employee.job_title else None

    # Late and overtime
    def get_late_minutes(self, obj):
        return obj.late_minutes() if obj else 0

    def get_overtime_minutes(self, obj):
        return obj.overtime_minutes() if obj else 0
