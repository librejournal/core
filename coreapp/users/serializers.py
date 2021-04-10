from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.base_user import BaseUserManager

from rest_framework import serializers
from rest_framework.authtoken.models import Token

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "uuid",
            "type",
            "username",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
        ]


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=300, required=True)
    password = serializers.CharField(required=True, write_only=True)


class AuthUserSerializer(UserSerializer):
    token = serializers.SerializerMethodField()

    def get_token(self, obj):
        token = None
        if obj.is_email_verified:
            token, _ = Token.objects.get_or_create(user=obj)
        return getattr(token, "key")

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + [
            "token",
        ]
        read_only_fields = [
            "id",
            "uuid",
            "is_active",
            "is_staff",
            "token",
        ]


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    A user serializer for registering the user
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
        ]
        read_only_fields = [
            "id",
        ]

    def validate_email(self, value):
        user = User.objects.filter(email=value)
        if user:
            raise serializers.ValidationError("Email is already taken")
        return BaseUserManager.normalize_email(value)

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user