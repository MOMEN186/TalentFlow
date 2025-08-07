from rest_framework import serializers
from .models import PayRoll,Department,JobTitle,Employee,LeaveNote

class PayRollSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="employee.first_name", read_only=True)
    middle_name = serializers.CharField(source="employee.middle_name", read_only=True)
    last_name = serializers.CharField(source="employee.last_name", read_only=True)
    class Meta:
        model = PayRoll
        fields = '__all__'
    def get_first_name(self, obj):
        return obj.employee.first_name if hasattr(obj, 'employee') else None

    def get_middle_name(self, obj):
        return obj.employee.middle_name if hasattr(obj, 'employee') else None

    def get_last_name(self, obj):
        return obj.employee.last_name if hasattr(obj, 'employee') else None

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

class JobTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTitle
        fields = ['id', 'name']
class LeaveNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveNote
        fields = '__all__'

     
class EmployeeSerializer(serializers.ModelSerializer):
    salary = PayRollSerializer(read_only=True)
    job_title = JobTitleSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    class Meta:
        model = Employee
        fields = [
            "id",
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "phone",
            "department",
            "job_title",
            "salary",
            "date_joined"
        ]       