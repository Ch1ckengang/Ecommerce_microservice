from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from user_service.api import success_response
from .serializers import UserRegistrationSerializer, UserSerializer
from .services import UserService


class RegisterView(GenericAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserService.register_user(serializer.validated_data)
        output = UserSerializer(user)
        return success_response(output.data, message="User registered successfully.", status_code=status.HTTP_201_CREATED)


class ProfileView(GenericAPIView):
    serializer_class = UserSerializer

    def get(self, request):
        serializer = self.get_serializer(request.user)
        return success_response(serializer.data, message="Profile fetched successfully.")

    def put(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        user = UserService.update_user(request.user, serializer.validated_data)
        output = self.get_serializer(user)
        return success_response(output.data, message="Profile updated successfully.")


class UserTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return success_response(serializer.validated_data, message="Token issued successfully.")


class UserTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return success_response(serializer.validated_data, message="Token refreshed successfully.")
