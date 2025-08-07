from ..models import Employee
from rest_framework import viewsets, status
from rest_framework.response import Response
from ..serializers import EmployeeSerializer

class EmployeeViewSet(viewsets.ModelViewSet):

    queryset = Employee.objects.all().select_related(
        "department",
        "job_title",
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

    