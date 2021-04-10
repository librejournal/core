from django.contrib.auth import logout, login
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from coreapp.users import serializers
from coreapp.users.utils import get_and_authenticate_user
from coreapp.utils.serializers import EmptySerializer


class LoggedInUserViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.request.user


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [
        AllowAny,
    ]
    serializer_class = EmptySerializer
    serializer_classes = {
        "login": serializers.LoginSerializer,
        "register": serializers.UserRegisterSerializer,
        # "password_change": serializers.PasswordChangeSerializer,
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
        return Response(data=data, status=status.HTTP_200_OK)

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
        data = serializers.AuthUserSerializer(user).data
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

    # @action(
    #     methods=[
    #         "POST",
    #     ],
    #     detail=False,
    #     permission_classes=[IsAuthenticated],
    # )
    # def password_change(self, request):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user = request.user
    #     serializer.update(user, serializer.data)
    #     return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")

        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()
