# accounts/urls.py
from django.urls import path, include
from .views import logout_view, ProfileViewSet, MyTokenObtainPairView, MyTokenRefreshView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')

urlpatterns = [
    path("login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", MyTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", logout_view, name="logout"),
    path("", include(router.urls)),  # This includes the router URLs
]