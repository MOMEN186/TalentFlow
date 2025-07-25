from rest_framework import serializers
from .models import LeaveRequest
from employees.models import Employee
from accounts.models import CustomUser


class EmployeeBasicSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    department_name = serializers.CharField(source='department.name', read_only=True)
    job_title_name = serializers.CharField(source='job_title.name', read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'department_name', 'job_title_name', 'annual_leave_balance']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_details = EmployeeBasicSerializer(source='employee', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.username', read_only=True)
    days_requested = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee_details', 'leave_type', 'start_date',
            'end_date', 'reason', 'status', 'approved_by', 'approved_by_name',
            'request_date', 'days_requested'
        ]
        read_only_fields = ['approved_by', 'request_date']

    def get_days_requested(self, obj):
        return (obj.end_date - obj.start_date).days + 1

    def validate(self, data):
        # Validate date range
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date cannot be after end date.")

        # Calculate days and validate max 21 days
        days_requested = (data['end_date'] - data['start_date']).days + 1
        if days_requested > 21:
            raise serializers.ValidationError("Leave request cannot exceed 21 days.")

        return data

    def create(self, validated_data):
        # Set employee from request user
        request = self.context['request']
        try:
            employee = Employee.objects.get(user=request.user)
            validated_data['employee'] = employee
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee profile not found for current user.")

        return super().create(validated_data)


class LeaveRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']

    def validate(self, data):
        # Validate date range
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date cannot be after end date.")

        # Calculate days and validate max 21 days
        days_requested = (data['end_date'] - data['start_date']).days + 1
        if days_requested > 21:
            raise serializers.ValidationError("Leave request cannot exceed 21 days.")

        return data


class LeaveRequestApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['status']

    def validate_status(self, value):
        if value not in ['Approved', 'Rejected']:
            raise serializers.ValidationError("Status must be either 'Approved' or 'Rejected'.")
        return value

    def update(self, instance, validated_data):
        request = self.context['request']

        # Set approved_by to current user
        instance.approved_by = request.user
        instance.status = validated_data['status']

        # If approved, decrease annual leave balance
        if validated_data['status'] == 'Approved':
            days_requested = (instance.end_date - instance.start_date).days + 1
            employee = instance.employee

            # Check if employee has enough balance
            if employee.annual_leave_balance < days_requested:
                raise serializers.ValidationError(
                    f"Employee doesn't have enough annual leave balance. "
                    f"Required: {days_requested}, Available: {employee.annual_leave_balance}"
                )

            employee.annual_leave_balance -= days_requested
            employee.save()

        instance.save()
        return instance