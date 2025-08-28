# attendance/views.py

from rest_framework import viewsets
from .models import Attendance
from .serializers import AttendanceSerializer, AttendanceCreateUpdateSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    # تعيين serializer الافتراضي ليكون serializer القراءة فقط.
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        # هذا هو الـ queryset الأصلي، غير المصفى. سيعيد جميع سجلات الحضور.
        return (
            Attendance.objects
            .select_related("employee", "employee__department", "employee__job_title")
            .order_by("-date")
        )

    # استخدام serializer الصحيح لكل عملية.
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AttendanceCreateUpdateSerializer
        return AttendanceSerializer

    # تم إزالة إجراء 'soft_delete' بالكامل لأنه يتم التعامل معه الآن من الواجهة الأمامية.