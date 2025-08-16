
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PayRollViewSet # adjust import to your view

router = DefaultRouter()

router.register(r"payroll", PayRollViewSet, basename="payroll")

urlpatterns = [
    path('', include(router.urls)),
]