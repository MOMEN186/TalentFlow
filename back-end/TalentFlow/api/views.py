import time
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Employee,LeaveNote
from .serializers import EmployeeSerializer,LeaveNoteSerializer
from django.utils.timezone import now

class EmployeeViewSet(viewsets.ModelViewSet):
    """
    A ModelViewSet providing default CRUD operations for Employee,
    plus a custom payroll endpoint at `/employees/payroll/`.
    """
    queryset = Employee.objects.all().select_related(
        "salary",
        "department",
        "job_title",
    )
    serializer_class = EmployeeSerializer

    @action(detail=False, methods=['get'], url_path='')
    def payroll(self, request):
        """
        GET /employees/payroll/
        Returns all employees with related salary, department, and job_title.
        """
        t0 = time.time()
        qs = self.get_queryset()
        t1 = time.time()
        serializer = self.get_serializer(qs, many=True)
        t2 = time.time()

        # Optional timing logs
        print(f"query time: {(t1 - t0) * 1000:.2f} ms")
        print(f"serialization time: {(t2 - t1) * 1000:.2f} ms")
        print(f"total payroll action time: {(time.time() - t0) * 1000:.2f} ms")

        return Response({"payroll": serializer.data}, status=status.HTTP_200_OK)

    # Override retrieve to return custom key
    def retrieve(self, request, pk=None):
        """
        GET /employees/{pk}/
        Returns single employee data under 'employee' key.
        """
        employee = self.get_object()
        serializer = self.get_serializer(employee)
        return Response(
            {"employee": serializer.data},
            status=status.HTTP_200_OK
        )
    @action(detail=False, methods=["get"], url_path="leave_notes")
    def leaveNote(self,request):
        query=LeaveNote.objects.select_related('employee').filter(date__gt=now().date())
        serializer=LeaveNoteSerializer(query,many=True)
        return Response(serializer.data)