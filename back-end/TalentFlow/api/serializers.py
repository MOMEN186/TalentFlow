from rest_framework import serializers
from .models import PayRoll,Department,JobTitle,Employee,LeaveNote

class PayRollSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayRoll
        fields = '__all__'

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