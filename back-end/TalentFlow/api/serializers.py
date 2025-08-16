# api/serializers.py
from rest_framework import serializers
from .models import Department,JobTitle,Employee,LeaveNote
from hr.serializers import PayRollSerializer


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
    salary = PayRollSerializer(source="payrolls",read_only=True,many=True)
    job_title = JobTitleSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    class Meta:
        model = Employee
        fields = "__all__"
        
    