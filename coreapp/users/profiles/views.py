from django.core.exceptions import ImproperlyConfigured
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from coreapp.users.models import Profile
from coreapp.users.profiles.serializers import (
    ProfileSerializer,
    FollowUnfollowSerializer,
)
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

    def _profile_response_with_pk(self, profile_pk):
        profile = get_object_or_404(Profile, pk=profile_pk)
        serializer = self.get_serializer(profile)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=[
            "GET",
        ],
        detail=True,
        url_path="detail",
        url_name="profile-detail-with-pk",
    )
    def profile_with_pk(self, request, *args, **kwargs):
        #api/profile/<id>/detail GET
        profile_pk = kwargs.get("pk")
        return self._profile_response_with_pk(profile_pk)

    @action(
        methods=[
            "GET",
        ],
        detail=False,
        url_path="self-detail",
        url_name="profile-detail",
    )
    def profile_from_request_user(self, request, *args, **kwargs):
        #api/profile/self-detail GET
        profile_pk = getattr(
            getattr(
                request.user,
                "profile",
                None,
            ),
            "id",
            None,
        )
        return self._profile_response_with_pk(profile_pk)

    @action(
        methods=[
            "PATCH",
        ],
        detail=False,
    )
    def follow(self, request, *args, **kwargs):
        # api/profile/follow
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
    def unfollow(self, request, *args, **kwargs):
        # api/profile/unfollow
        profile = getattr(request.user, "profile", None)
        if not profile:
            raise NotFound("Profile not found.")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.unfollow_with_profile(profile, serializer.data)
        return Response(status=status.HTTP_200_OK)
