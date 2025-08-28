# api/serializers.py
from rest_framework import serializers
from .models import Department,JobTitle,Employee,LeaveNote,Exit
from TalentFlow.accounts.models import CustomUser
from hr.serializers import PayRollSerializer
from decimal import Decimal

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

class JobTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTitle
        fields = ['id', 'name']

class LeaveNoteSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='employee.name', read_only=True)
    employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        required=True
    )
    class Meta:
        model = LeaveNote
        fields = '__all__'

     
class EmployeeSerializer(serializers.ModelSerializer):
    salary = PayRollSerializer(source="payrolls",read_only=True,many=True)
    job_title = JobTitleSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    is_hr = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Employee
        fields = (
            'id', 'first_name', 'last_name', 'middle_name', 'gender',
            'phone', 'address', 'department', 'job_title', 'status',
            'email', 'is_hr', 'date_joined', 'termination_date', 'salary'
        )

    def get_is_hr(self, obj):
        if obj.user:
            return obj.user.groups.filter(name='HR').exists()
        return False
        
    
class ExitSerializer(serializers.ModelSerializer):
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), source="employee", write_only=True
    )
    employee = serializers.StringRelatedField(read_only=True)
    recorded_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Exit
        fields = [
            "id",
            "employee",
            "employee_id",
            "exit_date",
            "exit_type",
            "reason",
            "notes",
            "final_settlement_amount",
            "recorded_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "employee", "recorded_by", "created_at", "updated_at"]

    def validate_exit_date(self, value):
        # ensure exit_date is not before employee's join date
        employee = self.initial_data.get("employee_id") or self.initial_data.get("employee")
        # employee is an id at this stage; ensure we fetch actual Employee instance
        emp = None
        if employee:
            try:
                emp = Employee.objects.get(pk=employee)
            except Exception:
                # let the FK field validation handle non-existent employee
                emp = None

        if emp and emp.date_joined and value < emp.date_joined:
            raise serializers.ValidationError("Exit date cannot be earlier than employee's join date.")
        # optional: prevent future-dated exits (business choice)
        # if value > timezone.localdate():
        #     raise serializers.ValidationError("Exit date cannot be in the future.")
        return value

    def validate_final_settlement_amount(self, value):
        if value is None:
            return value
        if isinstance(value, Decimal):
            if value < Decimal("0.00"):
                raise serializers.ValidationError("final_settlement_amount must be non-negative.")
        else:
            try:
                val = Decimal(value)
                if val < 0:
                    raise serializers.ValidationError("final_settlement_amount must be non-negative.")
            except Exception:
                raise serializers.ValidationError("Invalid decimal value for final_settlement_amount.")
        return value


class EmployeeCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Employee
        fields = [
            'first_name', 'last_name', 'middle_name', 'gender', 'phone', 'address', 
            'department', 'job_title', 'email', 'password', 'status'
        ]


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        
        fields = [
            'first_name', 'last_name', 'middle_name', 'gender', 'phone', 'address', 
            'department', 'job_title', 'status' 
        ]