from ..models import Employee , PayRoll
from rest_framework import viewsets, status
from rest_framework.response import Response
from ..serializers import EmployeeSerializer
from django.db.models import Prefetch

class EmployeeViewSet(viewsets.ModelViewSet):

    queryset = Employee.objects.select_related("department","job_title").prefetch_related(
        Prefetch("payrolls", queryset=PayRoll.objects.order_by("-date"))
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

    