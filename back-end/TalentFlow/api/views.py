from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
class EmployeeViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response({"message": "This is a placeholder."})


@api_view(["POST","GET"])
def getPayRoll(req):
    return Response("This is a placeholder")