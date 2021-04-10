from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


def get_username_from_email(email):
    user = User.objects.filter(email=email).first()
    if user:
        return user.username
    return None


def get_and_authenticate_user(email, password):
    username = get_username_from_email(email)
    user = authenticate(username=username, password=password)
    if user is None:
        raise serializers.ValidationError(
            "Invalid username/password. Please try again."
        )
    return user
