# serializers.py
from rest_framework import serializers
from .models import PayRoll
from TalentFlow.api.models import Employee  # adjust import path if different

class EmployeeMiniSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source="department.name", read_only=True)
    job_title = serializers.CharField(source="job_title.name", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Employee
        fields = (
            "id",
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "phone",
            "department",
            "job_title",
        )

class PayRollSerializer(serializers.ModelSerializer):
    # nested serializer instead of SerializerMethodField
    employee = EmployeeMiniSerializer(read_only=True)

    class Meta:
        model = PayRoll
        fields = "__all__"
