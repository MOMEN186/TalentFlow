# accounts/urls.py
from django.urls import path
from .views import logout_view, upload_photo  
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("logout/", logout_view, name="logout")  ,
    path("profile_photo/",upload_photo,name="upload_photo")
]
 