
from rest_framework import serializers
# from .models import Department,JobTitle,Employee,LeaveNote,Attendance
from .models import PayRoll
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
