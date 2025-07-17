from rest_framework import viewsets
from rest_framework.response import Response

class EmployeeViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response({"message": "This is a placeholder."})
