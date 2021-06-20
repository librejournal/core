from django.core.exceptions import ImproperlyConfigured
from django.db.models import F
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404, GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django_filters import rest_framework as filters
from rest_framework.viewsets import ModelViewSet

from coreapp.stories.view_mixins import RequestUserProfileMixin
from coreapp.users.models import Profile, ProfileReferrals, PROFILE_TYPE_CHOICES
from coreapp.users.profiles.filters import ProfileFilter
from coreapp.users.profiles.permissions import HasReferralsLeft
from coreapp.users.profiles.serializers import (
    DetailedProfileSerializer,
    ProfileSerializer,
    FollowUnfollowSerializer,
    TinyProfileSerializer,
    ReferralSerializer,
    RenderProfileSerializer,
    ProfileReferralSerializer,
)
from coreapp.utils.pagination import CustomLimitOffsetPagination
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
    pagination_class = CustomLimitOffsetPagination

    def get_serializer_class(self):
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping.")

        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()

    def _profile_response(self, profile_pk, serializer_class):
        def _get_serializer(*args, **kwargs):
            kwargs.setdefault("context", self.get_serializer_context())
            return serializer_class(*args, **kwargs)

        profile = get_object_or_404(Profile, pk=profile_pk)
        serializer = _get_serializer(profile)
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
        # api/profile/<id>/detail GET
        profile_pk = kwargs.get("pk")
        return self._profile_response(profile_pk, ProfileSerializer)

    @action(
        methods=[
            "GET",
        ],
        detail=False,
        url_path="self-detail",
        url_name="profile-detail",
    )
    def profile_from_request_user(self, request, *args, **kwargs):
        # api/profile/self-detail GET
        profile_pk = getattr(
            getattr(
                request.user,
                "profile",
                None,
            ),
            "id",
            None,
        )
        return self._profile_response(profile_pk, DetailedProfileSerializer)

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


class TinyProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = TinyProfileSerializer
    pagination_class = CustomLimitOffsetPagination

    filterset_class = ProfileFilter
    filter_backends = (filters.DjangoFilterBackend,)

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(
            profile_score=F("profilestatistics__reputation"),
        )
        return qs


class GenericFollowUnFollowView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowUnfollowSerializer

    action_type = None

    @property
    def profile(self):
        profile = getattr(self.request.user, "profile", None)
        if not profile:
            raise NotFound("Profile not found.")
        return profile

    def _follow(self):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.follow_with_profile(self.profile, serializer.data)

    def _unfollow(self):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.unfollow_with_profile(self.profile, serializer.data)

    def patch(self, request, *args, **kwargs):
        processor = getattr(self, f"_{self.action_type}", None)
        processor()
        return Response(status=status.HTTP_200_OK)


class FollowView(GenericFollowUnFollowView):
    action_type = "follow"


class UnfollowView(GenericFollowUnFollowView):
    action_type = "unfollow"


class GenericProfileView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    response_serializer_class = None

    def _get_profile_pk(self):
        pass

    def _get_serializer(self, *args, **kwargs):
        kwargs.setdefault("context", self.get_serializer_context())
        return self.response_serializer_class(*args, **kwargs)

    def _get_profile_response(self):
        profile_pk = self._get_profile_pk()
        profile = get_object_or_404(Profile, pk=profile_pk)
        serializer = self._get_serializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        return self._get_profile_response()


class SelfProfileView(GenericProfileView):
    response_serializer_class = DetailedProfileSerializer

    def _get_profile_pk(self):
        return getattr(
            getattr(
                self.request.user,
                "profile",
                None,
            ),
            "id",
            None,
        )


class ProfileWithPkView(GenericProfileView):
    response_serializer_class = ProfileSerializer

    def _get_profile_pk(self):
        return self.kwargs.get("pk")


class AcceptWriterInviteView(GenericAPIView, RequestUserProfileMixin):
    permission_classes = [IsAuthenticated]

    def post(self, *args, **kwargs):
        referral = get_object_or_404(
            ProfileReferrals, to_profile=self.profile, accepted=False
        )
        referral.accepted = True
        self.profile.type = PROFILE_TYPE_CHOICES.WRITER
        referral.save()
        self.profile.save()
        return Response(status=status.HTTP_200_OK)


class ProfileReferralsViewSet(ModelViewSet, RequestUserProfileMixin):
    authentication_classes = [IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination
    lookup_field = "id"
    lookup_url_kwarg = "id"

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RenderProfileSerializer
        return ProfileReferralSerializer

    def get_queryset(self):
        # get request profile's not accepted sent invites
        return ProfileReferrals.objects.filter(
            referred_by=self.profile,
            accepted=False,
        )

    def create(self, request, *args, **kwargs):
        if not HasReferralsLeft().has_permission(request, self):
            return Response(
                data="No more referrals left...", status=status.HTTP_403_FORBIDDEN
            )
        request_data = {**request.data}
        request_data["referred_by"] = self.profile_id
        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(status=status.HTTP_201_CREATED, headers=headers)


class ProfileFollowingListView(ListAPIView, RequestUserProfileMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = TinyProfileSerializer
    pagination_class = CustomLimitOffsetPagination

    def get_profile(self):
        return self.profile

    def get_queryset(self):
        return self.get_profile().followed_authors.all()


class ProfileFollowersListView(ListAPIView, RequestUserProfileMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = TinyProfileSerializer
    pagination_class = CustomLimitOffsetPagination

    def get_profile(self):
        return self.profile

    def get_queryset(self):
        return self.get_profile().followed_by.all()
