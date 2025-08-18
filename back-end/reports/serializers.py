from rest_framework import serializers
from TalentFlow.api.models import Employee, LeaveNote, JobTitle, Department
from attendance.models import Attendance
from hr.models import PayRoll


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name"]


class JobTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTitle
        fields = ["id", "title", "department"]


class EmployeeSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    job_title = JobTitleSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id", "first_name", "middle_name", "last_name",
            "email", "phone", "hire_date", "department", "job_title"
        ]


class AttendanceSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = [
            "id", "employee", "check_in", "check_out", "status", "date"
        ]


class LeaveNoteSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = LeaveNote
        fields = ["id", "first_name","employee", "date", "return_date", "description"]


class PayRollSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)

    class Meta:
        model = PayRoll
        fields = ["id", "employee", "basic_salary", "allowances", "deductions", "net_salary", "month", "year"]
