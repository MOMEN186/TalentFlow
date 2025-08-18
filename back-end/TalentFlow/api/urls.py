#api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet ,LeaveNoteViewSet ,ExitViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employees')
router.register(r"leave_notes", LeaveNoteViewSet, basename="leave_notes")
router.register(r"exit", ExitViewSet, basename="exit")

urlpatterns = [
    path('', include(router.urls)),
]