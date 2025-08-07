from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet ,PayRollViewSet,LeaveNoteViewSet # adjust import to your view

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employees')
router.register(r"payroll", PayRollViewSet, basename="payroll")
router.register(r"leave_notes", LeaveNoteViewSet, basename="leave_notes")
urlpatterns = [
    path('', include(router.urls)),
]