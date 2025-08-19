# attendance/views.py
from rest_framework import viewsets
from .models import Attendance
from .serializers import AttendanceSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    def get_queryset(self):
        return (
            Attendance.objects
            .select_related("employee", "employee__department", "employee__job_title")
            .order_by("-date")   # keep ordering but ensure index exists
        )
