from rest_framework import serializers
from .models import PayRoll,Department,JobTitle,Employee,LeaveNote

class PayRollSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()
    class Meta:
        model = PayRoll
        fields = '__all__'
        
    def get_employee(self, obj):
        emp=obj.employee
        if not emp:
            return None
        return {
            "id": emp.id,
            "first_name": emp.first_name,
            "middle_name": emp.middle_name,
            "last_name": emp.last_name,
            "email": emp.email,
            "phone": emp.phone,
            "department": emp.department.name if emp.department else None,
            "job_title": emp.job_title.name if emp.job_title else None,
        }

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