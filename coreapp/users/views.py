from django.contrib.auth import logout, login, get_user_model
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from coreapp.users import serializers
from coreapp.users.models import GenericToken, TOKEN_TYPE_CHOICES
from coreapp.users.tasks import send_simple_password_reset_mail_task
from coreapp.users.utils import get_and_authenticate_user
from coreapp.users.permissions import IsUserVerified
from coreapp.users.verification.email import (
    build_password_reset_url,
    send_simple_password_reset_with_url,
)

User = get_user_model()


class LoggedInUserViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        IsUserVerified,
    ]
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.request.user


class VerificationView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.VerificationSerializer

    @property
    def token(self):
        key = self.request.query_params.get("token", None)
        token = GenericToken.objects.filter(
            key=key,
        ).first()
        if not token:
            raise NotFound("Token not found.")
        if not token.is_valid_key:
            raise ValidationError("Token is invalid.")
        return token

    @property
    def token_user(self):
        return self.token.user

    def get(self, request, *args, **kwargs):
        token = self.token
        user = token.user
        user.verify_user(token)
        return Response(data={"is_verified": True}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.save()
        return Response({"token": token.key}, status=status.HTTP_201_CREATED)


class LoginView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_and_authenticate_user(
            serializer.validated_data["email"], serializer.validated_data["password"]
        )
        login(request, user)
        data = serializers.AuthUserSerializer(user).data
        return Response(data={"token": data["token"]}, status=status.HTTP_200_OK)


class RegisterView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.UserRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = serializers.UserSerializer(user).data
        return Response(data=data, status=status.HTTP_201_CREATED)


class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response(status=status.HTTP_200_OK)


class PasswordResetView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.PasswordResetSerializer

    def get(self, request, *args, **kwargs):
        email = request.query_params.get("email", None)
        user = get_object_or_404(User, email=email)

        pwd_reset_token = user.get_or_create_token_with_type(
            type=TOKEN_TYPE_CHOICES.PASSWORD_RESET,
        )

        url = build_password_reset_url(pwd_reset_token.key)
        send_simple_password_reset_mail_task.delay(
            user.email,
            pwd_reset_token.key,
            url,
        )

        return Response(status=status.HTTP_201_CREATED)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_from_request = serializer.data["token"]
        generic_token = GenericToken.objects.filter(key=token_from_request).first()
        if not generic_token:
            return Response(status=status.HTTP_403_FORBIDDEN)

        user = generic_token.user
        new_password = serializer.data["password"]
        user.set_password(new_password)
        user.save()

        return Response(status=status.HTTP_200_OK)
