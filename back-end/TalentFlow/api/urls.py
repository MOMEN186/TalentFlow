#api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, DepartmentViewSet, JobTitleViewSet, ExitViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employees')
# router.register(r"leave_notes", LeaveNoteViewSet, basename="leave_notes")
router.register(r"exits", ExitViewSet, basename="exit")
router.register(r'departments', DepartmentViewSet, basename='departments') 
router.register(r'job-titles', JobTitleViewSet, basename='job-titles') 

urlpatterns = [
    path('', include(router.urls)),
    path('employees/<int:pk>/leave-notes/', EmployeeViewSet.as_view({'get': 'leave_notes'}), name='employee-leave-notes'),
    path('employees/<int:pk>/exit-records/', EmployeeViewSet.as_view({'get': 'exit_records'}), name='employee-exit-records'),
]