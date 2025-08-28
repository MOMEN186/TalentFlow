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
    # حقول late_minutes و overtime_minutes يتم التعامل معها تلقائيا بواسطة دوال النموذج
    # لذلك لا نحتاج إلى SerializerMethodField هنا.

    class Meta:
        model = Attendance
        fields = "__all__"


class AttendanceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'check_in', 'check_out']

    def create(self, validated_data):
        # 1. Pop the 'employee' ID from the validated data.
        employee_id = validated_data.pop('employee')
        
        # 2. Get the actual Employee object from the database using the ID.
        try:
            employee = Employee.objects.get(pk=employee_id)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee not found.")

        # 3. Create the Attendance record with the actual Employee object.
        attendance = Attendance.objects.create(employee=employee, **validated_data)
        return attendance

    def update(self, instance, validated_data):
        # Handle the update process similarly
        if 'employee' in validated_data:
            employee_id = validated_data.pop('employee')
            try:
                instance.employee = Employee.objects.get(pk=employee_id)
            except Employee.DoesNotExist:
                raise serializers.ValidationError("Employee not found.")
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance