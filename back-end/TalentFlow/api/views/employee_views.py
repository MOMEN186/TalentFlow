# api/views/employee_views.py
from ..models import Employee 
from hr.models import PayRoll
from rest_framework import viewsets, status
from rest_framework.response import Response
from ..serializers import EmployeeSerializer
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

class EmployeeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Employee.objects.select_related(
        "department", "job_title"
    ).prefetch_related(
        Prefetch("payrolls", queryset=PayRoll.objects.order_by("-month", "-year"))
    )
    serializer_class = EmployeeSerializer

    # Override retrieve to return custom key
    def retrieve(self, request, pk=None):
        """
        GET /employees/{pk}/
        Returns single employee data under 'employee' key.
        """
        employee = self.get_object()
        serializer = self.get_serializer(employee)
        return Response({"employee": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="me" ,url_name="me")
    def me(self, request):
        """
        GET /employees/me/
        Returns the Employee record associated with the authenticated user.
        """
        user = request.user

        # Option A: common case — Employee has a FK/OneToOne to the User model (field name "user")
        try:
            employee = get_object_or_404(Employee, user=user)
        except Exception:
            # Option B: if your Employee model stores the user id in a different field,
            # try matching by `user_id` or whatever field you use:
            # employee = get_object_or_404(Employee, user_id=user.id)
            return Response(
                {"detail": "Employee record not found for the current user."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(employee)
        return Response({"employee": serializer.data}, status=status.HTTP_200_OK)