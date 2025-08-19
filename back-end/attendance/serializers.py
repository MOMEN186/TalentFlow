from rest_framework import serializers
from .models import Attendance
from TalentFlow.api.models import Employee
class EmployeeMiniSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source="department.name", read_only=True)
    job_title = serializers.CharField(source="job_title.name", read_only=True)
  

    class Meta:
        model = Employee
        fields = (
            "id",
            "first_name",
            "middle_name",
            "last_name",
            "department",
            "job_title",
        )


class AttendanceSerializer(serializers.ModelSerializer):
    employee = EmployeeMiniSerializer(read_only=True)
    late_minutes = serializers.SerializerMethodField()
    overtime_minutes = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields ="__all__"

    def get_late_minutes(self, obj):
        return obj.late_minutes() if obj else 0

    def get_overtime_minutes(self, obj):
        return obj.overtime_minutes() if obj else 0