from django.contrib.auth import logout, login
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from coreapp.users import serializers
from coreapp.users.models import GenericToken
from coreapp.users.utils import get_and_authenticate_user
from coreapp.users.permissions import IsUserNotVerifiedYet, IsUserVerified
from coreapp.utils.serializers import EmptySerializer


class LoggedInUserViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.request.user


class VerificationView(GenericAPIView):
    permission_classes = [IsUserNotVerifiedYet]
    serializer_class = serializers.VerificationSerializer

    def get(self, request, *args, **kwargs):
        key = self.kwargs.get("token", None)
        token = GenericToken.objects.filter(
            key=key,
        ).first()
        if not token:
            raise NotFound("Token not found.")
        if not token.is_valid_key:
            raise ValidationError("Token is invalid.")
        user = token.user
        user.verify_user(token)
        return Response(None, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.save()
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [
        AllowAny,
    ]
    serializer_class = EmptySerializer
    serializer_classes = {
        "login": serializers.LoginSerializer,
        "register": serializers.UserRegisterSerializer,
    }

    @action(
        methods=[
            "POST",
        ],
        detail=False,
    )
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_and_authenticate_user(
            serializer.validated_data["email"], serializer.validated_data["password"]
        )
        login(request, user)
        data = serializers.AuthUserSerializer(user).data
        return Response(data={"token": data["token"]}, status=status.HTTP_200_OK)

    @action(
        methods=[
            "POST",
        ],
        detail=False,
    )
    @transaction.atomic
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = serializers.UserSerializer(user).data
        return Response(data=data, status=status.HTTP_201_CREATED)

    @action(
        methods=[
            "POST",
        ],
        detail=False,
    )
    def logout(self, request):
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response(status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")

        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()
