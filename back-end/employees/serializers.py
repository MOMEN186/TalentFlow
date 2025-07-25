from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Department, JobTitle, Employee

User = get_user_model()


class DepartmentSerializer(serializers.ModelSerializer):
    manager_name = serializers.SerializerMethodField()
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'manager', 'manager_name', 'employee_count']

    def get_manager_name(self, obj):
        if obj.manager:
            # First try to get the manager's employee record for first_name and last_name
            try:
                employee = Employee.objects.get(user=obj.manager)
                return f"{employee.first_name} {employee.last_name}".strip()
            except Employee.DoesNotExist:
                # Fallback to CustomUser fields if they exist
                if hasattr(obj.manager, 'first_name') and hasattr(obj.manager, 'last_name'):
                    first_name = getattr(obj.manager, 'first_name', '').strip()
                    last_name = getattr(obj.manager, 'last_name', '').strip()
                    if first_name or last_name:
                        return f"{first_name} {last_name}".strip()
                # Final fallback to username
                return getattr(obj.manager, 'username', str(obj.manager))
        return None

    def get_employee_count(self, obj):
        return obj.employees.count()

    def validate_manager(self, value):
        """Validate that the manager exists and is active"""
        if value:
            if not value.is_active:
                raise serializers.ValidationError("Manager must be an active user.")
        return value


class JobTitleSerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = JobTitle
        fields = ['id', 'name', 'description', 'employee_count']

    def get_employee_count(self, obj):
        return obj.employees.count()


class EmployeeListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    job_title_name = serializers.CharField(source='job_title.name', read_only=True)
    full_name = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'user_email', 'first_name', 'last_name', 'full_name',
            'date_of_birth', 'gender', 'phone', 'hire_date',
            'national_id', 'marital_status', 'is_active',
            'department', 'department_name', 'job_title', 'job_title_name'
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class EmployeeDetailSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    job_title_name = serializers.CharField(source='job_title.name', read_only=True)
    # department_details = DepartmentSerializer(source='department', read_only=True)
    # job_title_details = JobTitleSerializer(source='job_title', read_only=True)
    full_name = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'user_email', 'user_username', 'first_name', 'last_name', 'full_name',
            'date_of_birth', 'gender', 'phone', 'address', 'hire_date',
            'national_id', 'marital_status', 'emergency_contact',
            'annual_leave_balance', 'is_active', 'department', 'department_name',
            'job_title', 'job_title_name'
        ]
        # 'department_details', 'job_title_details'

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'user', 'first_name', 'last_name', 'date_of_birth', 'gender',
            'phone', 'address', 'hire_date', 'national_id', 'marital_status',
            'emergency_contact', 'annual_leave_balance', 'is_active',
            'department', 'job_title'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'date_of_birth': {'required': True},
            'gender': {'required': True},
            'phone': {'required': True},
            'address': {'required': True},
            'hire_date': {'required': True},
            'national_id': {'required': True},
            'marital_status': {'required': True},
            'annual_leave_balance': {'required': True},
            'department': {'required': True},
            'job_title': {'required': True},
        }

    def validate_user(self, value):
        """Check if user is already associated with another employee"""
        if self.instance:  # Update case
            if Employee.objects.filter(user=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("This user is already associated with another employee.")
        else:  # Create case
            if Employee.objects.filter(user=value).exists():
                raise serializers.ValidationError("This user is already associated with an employee.")

        # Validate user is active
        if not value.is_active:
            raise serializers.ValidationError("User must be active to be assigned as an employee.")

        return value

    def validate_phone(self, value):
        """Validate phone number format and uniqueness"""
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")

        if len(value) != 11:
            raise serializers.ValidationError("Phone number must be exactly 11 digits.")

        # Check uniqueness
        if self.instance:  # Update case
            if Employee.objects.filter(phone=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Employee with this phone number already exists.")
        else:  # Create case
            if Employee.objects.filter(phone=value).exists():
                raise serializers.ValidationError("Employee with this phone number already exists.")

        return value

    def validate_national_id(self, value):
        """Validate national ID format and uniqueness"""
        if not value.isdigit():
            raise serializers.ValidationError("National ID must contain only digits.")

        if len(value) != 14:
            raise serializers.ValidationError("National ID must be exactly 14 digits.")

        # Check uniqueness
        if self.instance:  # Update case
            if Employee.objects.filter(national_id=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Employee with this national ID already exists.")
        else:  # Create case
            if Employee.objects.filter(national_id=value).exists():
                raise serializers.ValidationError("Employee with this national ID already exists.")

        return value

    def validate_emergency_contact(self, value):
        """Validate emergency contact if provided"""
        if value:
            if not value.isdigit():
                raise serializers.ValidationError("Emergency contact must contain only digits.")
            if len(value) != 11:
                raise serializers.ValidationError("Emergency contact must be exactly 11 digits.")
        return value

    def validate_annual_leave_balance(self, value):
        """Validate annual leave balance"""
        if value < 0:
            raise serializers.ValidationError("Annual leave balance cannot be negative.")
        if value > 365:
            raise serializers.ValidationError("Annual leave balance cannot exceed 365 days.")
        return value

    def validate_department(self, value):
        """Validate department exists"""
        if not Department.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Selected department does not exist.")
        return value

    def validate_job_title(self, value):
        """Validate job title exists"""
        if not JobTitle.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Selected job title does not exist.")
        return value

    def validate(self, attrs):
        """Cross-field validation"""
        from datetime import date

        # Validate date of birth is not in the future
        if attrs.get('date_of_birth') and attrs['date_of_birth'] > date.today():
            raise serializers.ValidationError({
                'date_of_birth': 'Date of birth cannot be in the future.'
            })

        # Validate hire date is not in the future
        if attrs.get('hire_date') and attrs['hire_date'] > date.today():
            raise serializers.ValidationError({
                'hire_date': 'Hire date cannot be in the future.'
            })

        # Validate age (should be at least 18)
        if attrs.get('date_of_birth'):
            age = (date.today() - attrs['date_of_birth']).days / 365.25
            if age < 18:
                raise serializers.ValidationError({
                    'date_of_birth': 'Employee must be at least 18 years old.'
                })

        return attrs


# Additional serializers for specific use cases
class EmployeeSummarySerializer(serializers.ModelSerializer):
    """Minimal employee info for dropdowns/selections"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'first_name', 'last_name', 'full_name', 'is_active']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class DepartmentWithEmployeesSerializer(serializers.ModelSerializer):
    """Department with embedded employee list"""
    employees = EmployeeListSerializer(many=True, read_only=True)
    employee_count = serializers.SerializerMethodField()
    manager_name = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'manager', 'manager_name', 'employee_count', 'employees']

    def get_manager_name(self, obj):
        if obj.manager:
            if hasattr(obj.manager, 'first_name') and hasattr(obj.manager, 'last_name'):
                return f"{obj.manager.first_name} {obj.manager.last_name}".strip()
            return getattr(obj.manager, 'username', str(obj.manager))
        return None

    def get_employee_count(self, obj):
        return obj.employees.count()


class EmployeeBasicSerializer(serializers.ModelSerializer):
    # user = serializers.StringRelatedField()

    class Meta:
        model = Employee
        fields = ['id', 'first_name','last_name']