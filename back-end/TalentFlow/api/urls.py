from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet ,getPayRoll # adjust import to your view

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')

urlpatterns = [
    path('', include(router.urls)),
    path('payroll/',getPayRoll,name="get")
  
]