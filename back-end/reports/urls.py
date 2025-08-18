# ==============================================
# reports/urls.py
# ==============================================
from django.urls import path
from .views import  ReportsTurnoverAPIView

urlpatterns = [
    path("turnover/", ReportsTurnoverAPIView.as_view(), name="reports-turnover"),
]