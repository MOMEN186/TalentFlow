from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet  # adjust import to your view

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')

urlpatterns = [
    path('', include(router.urls)),
]