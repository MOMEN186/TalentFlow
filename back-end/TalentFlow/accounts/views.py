# accounts/views.py
import logging

from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)

from .serializers import UserSerializer
from .models import CustomUser  # <<-- fixed import (space after from)

logger = logging.getLogger(__name__)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh = response.data.pop("refresh", None)

        if refresh:
            response.set_cookie(
                "refresh_token",
                refresh,
                httponly=True,
                samesite="None" if not settings.DEBUG else "Lax",
                secure=not settings.DEBUG,
                max_age=60 * 60 * 24 * 7,
            )
        return response


class MyTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        # if there's no refresh in body, try cookie and inject it into a copy of the data
        data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        if not data.get("refresh"):
            cookie_token = request.COOKIES.get("refresh_token")
            if cookie_token:
                data["refresh"] = cookie_token

        # call serializer manually to avoid mutating request.data in unexpected ways
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        res_data = serializer.validated_data
        # Use the view's response machinery to generate tokens (TokenRefreshView normally returns)
        response = Response(res_data)

        new_refresh = res_data.get("refresh")
        if new_refresh:
            response.set_cookie(
                "refresh_token",
                new_refresh,
                httponly=True,
                secure=not settings.DEBUG,
                samesite="None" if not settings.DEBUG else "Lax",
                max_age=60 * 60 * 24 * 7,
            )
            response.data.pop("refresh", None)
        return response


@api_view(["POST"])
def logout_view(request):
    try:
        refresh_token = request.data.get("refresh") or request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"detail": "No refresh token provided"}, status=status.HTTP_400_BAD_REQUEST)

        token = RefreshToken(refresh_token)
        token.blacklist()

        response = Response({"detail": "Logout successful"})
        # Use basic delete_cookie for broad compatibility across Django versions
        response.delete_cookie("refresh_token")
        return response
    except TokenError:
        response = Response({"detail": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
        response.delete_cookie("refresh_token")
        return response


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="upload_photo",
        permission_classes=[IsAuthenticated],
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_photo(self, request):
        try:
            user = request.user

            # Ensure the user model actually has the field
            if not hasattr(user, "profile_photo"):
                logger.error("User model has no 'profile_photo' attribute")
                return Response({"error": "User does not support profile photos"}, status=status.HTTP_400_BAD_REQUEST)

            # Accept either 'image' or 'profile_photo' as the form key
            file_obj = request.FILES.get("image") or request.FILES.get("profile_photo")
            if not file_obj:
                return Response({"error": "No image file provided"}, status=status.HTTP_400_BAD_REQUEST)

            # Save file and user
            user.profile_photo = file_obj
            user.save(update_fields=["profile_photo"])

            # build absolute url (ensure MEDIA_URL is configured)
            photo_url = request.build_absolute_uri(user.profile_photo.url)
            return Response({"message": "Photo uploaded successfully.", "photo_url": photo_url}, status=status.HTTP_201_CREATED)

        except Exception as exc:
            logger.exception("Error while uploading profile photo: %s", exc)
            return Response({"error": "Failed to upload photo", "details": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
