# attendance/views.py
from rest_framework import viewsets
from .models import Attendance
from .serializers import AttendanceSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all().select_related("employee").order_by("-date")
    serializer_class = AttendanceSerializer
