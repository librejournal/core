from django.core.exceptions import ImproperlyConfigured
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from coreapp.users.profiles.serializers import ProfileSerializer, FollowUnfollowSerializer
from coreapp.utils.serializers import EmptySerializer


class ProfileView(viewsets.GenericViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = EmptySerializer
    serializer_classes = {
        "profile": ProfileSerializer,
        "follow": FollowUnfollowSerializer,
        "unfollow": FollowUnfollowSerializer,
    }

    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")

        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()

    @action(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def profile(self, request):
        profile = getattr(request.user, "profile", None)
        if not profile:
            raise NotFound("Profile not found.")
        serializer = self.get_serializer(profile)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=[
            "PATCH",
        ],
        detail=False,
    )
    def follow(self, request):
        profile = getattr(request.user, "profile", None)
        if not profile:
            raise NotFound("Profile not found.")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.follow_with_profile(profile, serializer.data)
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=[
            "PATCH",
        ],
        detail=False,
    )
    def unfollow(self, request):
        profile = getattr(request.user, "profile", None)
        if not profile:
            raise NotFound("Profile not found.")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.unfollow_with_profile(profile, serializer.data)
        return Response(status=status.HTTP_200_OK)
