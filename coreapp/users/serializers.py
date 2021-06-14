from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.base_user import BaseUserManager
from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token

from coreapp.users.models import (
    TOKEN_TYPE_CHOICES,
    UserVerification,
    Profile,
    ProfileReferrals,
)

User = get_user_model()


class TinyUserSerializer(serializers.ModelSerializer):
    profile_id = serializers.SerializerMethodField()

    def get_profile_id(self, obj):
        if isinstance(obj, dict):
            return None
        profile_id = getattr(
            getattr(
                obj,
                "profile",
                None,
            ),
            "id",
            None,
        )
        return profile_id

    class Meta:
        model = User
        fields = [
            "id",
            "uuid",
            "profile_id",
            "username",
        ]


class UserSerializer(serializers.ModelSerializer):
    profile_id = serializers.SerializerMethodField()
    has_pending_referral = serializers.SerializerMethodField()

    def get_profile_id(self, obj):
        if isinstance(obj, dict):
            return None
        profile_id = getattr(
            getattr(
                obj,
                "profile",
                None,
            ),
            "id",
            None,
        )
        return profile_id

    def get_has_pending_referral(self, obj):
        return ProfileReferrals.objects.filter(
            to_profile=obj.profile,
            accepted=False,
        ).exists()

    class Meta:
        model = User
        fields = [
            "id",
            "uuid",
            "profile_id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "has_pending_referral",
        ]


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=300, required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        user_verification = UserVerification.objects.filter(
            user__email=attrs["email"]
        ).first()
        if not user_verification or not user_verification.is_verified:
            raise ValidationError("User is not yet verified")
        return attrs


class AuthUserSerializer(UserSerializer):
    token = serializers.SerializerMethodField()

    def get_token(self, obj):
        token = None
        if obj.is_verified:
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

    @transaction.atomic
    def create(self, validated_data):
        # Create user
        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        user.refresh_from_db()

        # Create verification
        UserVerification.objects.get_or_create(user=user)

        # Create a profile as reader
        Profile.objects.get_or_create(user=user)

        return user


class VerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    type = serializers.ChoiceField(choices=TOKEN_TYPE_CHOICES)

    def validate(self, attrs):
        email = attrs["email"]
        user = User.objects.filter(email=email).first()
        if not user:
            raise ValidationError("User with email does not exist.")
        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        return user.get_or_create_verification_token(validated_data["type"])
