# accounts/views.py
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer  # Fixed typo: serialzer -> serializer

    def post(self, req, *args, **kwargs):
        response = super().post(req, *args, **kwargs)
        refresh = response.data.pop("refresh", None)

        if refresh:
            response.set_cookie(
                "refresh_token",
                refresh,
                httponly=True,
                samesite="None" if not settings.DEBUG else "Lax",  # Consistent samesite
                secure=not settings.DEBUG,  # Consistent secure setting
                max_age=60 * 60 * 24 * 7,  # 7 days
            )
        return response


class MyTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, req, *args, **kwargs):
        print("---------------------", req.data, "-----------------")
        
        # If no refresh token in body, try to get from cookie
        if not req.data.get("refresh"):
            cookie_token = req.COOKIES.get("refresh_token")
            if cookie_token:
                # Make request data mutable if it's not already
                if hasattr(req.data, "_mutable"):
                    req.data._mutable = True
                    req.data["refresh"] = cookie_token

        res = super().post(req, *args, **kwargs)
        
        # Get the new refresh token from response
        new_refresh = res.data.get("refresh")

        if new_refresh:
            # Set the new refresh token in cookie
            res.set_cookie(
                "refresh_token",
                new_refresh,  # Fixed: was missing the actual token value
                httponly=True,  # Fixed typo: httpOnly -> httponly
                secure=not settings.DEBUG,
                samesite="None" if not settings.DEBUG else "Lax",
                max_age=60 * 60 * 24 * 7,  # 7 days
            )
            # Remove refresh token from response body
            res.data.pop("refresh", None)
        
        return res


@api_view(["POST"])
def logout_view(request):
    try:
        # Try to get refresh token from request data first
        refresh_token = request.data.get("refresh")
        
        # If not in data, try to get from cookie
        if not refresh_token:
            refresh_token = request.COOKIES.get("refresh_token")
            
        if not refresh_token:
            return Response(
                {"detail": "No refresh token provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        # Create response and clear the cookie
        response = Response({"detail": "Logout successful"})
        response.delete_cookie(
            "refresh_token",
            samesite="None" if not settings.DEBUG else "Lax",
            secure=not settings.DEBUG
        )
        return response
        
    except TokenError:
        # Still clear the cookie even if token is invalid
        response = Response(
            {"detail": "Invalid or expired token"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        response.delete_cookie(
            "refresh_token",
            samesite="None" if not settings.DEBUG else "Lax",
            secure=not settings.DEBUG
        )
        return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_photo(req):
    try:
        print(f"User: {req.user}")
        print(f"Content-Type: {req.content_type}")
        print(f"Request FILES: {req.FILES}")
        print(f"Request DATA: {req.data}")
        
        user = req.user
        
        # Check if image file is provided
        if 'image' not in req.FILES:
            return Response(
                {"error": "No image file provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user.profile_photo = req.FILES["image"]
        user.save()
        
        photo_url = req.build_absolute_uri(user.profile_photo.url)
        return Response({
            "message": "Photo uploaded successfully.", 
            "photo_url": photo_url
        })
        
    except Exception as e:
        print(f"Upload error: {e}")
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )