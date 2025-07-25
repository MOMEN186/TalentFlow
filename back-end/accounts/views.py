from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import CustomUser
from .serializers import MyTokenObtainPairSerializer, ListUsersSerializer
from django.shortcuts import render

# Create your views here.


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# class ProfileView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         user = request.user
#         return Response({
#             "username": user.username,
#             "email": user.email,
#             "role": user.role,
#         })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ListUsersAPI(request):
    if request.method == 'GET':
        queryset = CustomUser.objects.all()
        serializer = ListUsersSerializer(queryset, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


