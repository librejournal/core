from django.contrib.auth import get_user_model

from rest_framework import serializers

from coreapp.users.models import Profile, PROFILE_TYPE_CHOICES, ProfileReferrals
from coreapp.users.serializers import UserSerializer, TinyUserSerializer
from coreapp.stories.models import StoryLocations, StoryTags
from coreapp.stories.serializers import StoryLocationSerializer, StoryTagsSerializer

User = get_user_model()


def _get_profile_score(serializer, profile):
    score_from_context = serializer.context.get("profile_score", None)
    if score_from_context:
        return score_from_context
    return getattr(profile, "weighted_profile_score", None)


class TinyProfileSerializer(serializers.ModelSerializer):
    user = TinyUserSerializer(read_only=True)
    score = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "id",
            "uuid",
            "type",
            "score",
            "user",
        ]

    def get_score(self, obj):
        return _get_profile_score(self, obj)


class DetailedProfileSerializer(serializers.ModelSerializer):
    followed_authors = TinyProfileSerializer(many=True, read_only=True)
    followed_locations = StoryLocationSerializer(many=True, read_only=True)
    followed_tags = StoryTagsSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    score = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "id",
            "uuid",
            "type",
            "score",
            "user",
            "followed_locations",
            "followed_authors",
            "followed_tags",
        ]

    def get_score(self, obj):
        return _get_profile_score(self, obj)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id",
            "uuid",
            "type",
            "user",
            "followed_locations",
            "followed_authors",
            "followed_tags",
        ]


class FollowUnfollowSerializer(serializers.Serializer):
    profile_id_list = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    story_location_id_list = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    story_tag_id_list = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )

    def get_id_lists(self, validated_data):
        return {
            "profile_id_list": validated_data.get("profile_id_list", []),
            "story_location_id_list": validated_data.get("story_location_id_list", []),
            "story_tag_id_list": validated_data.get("story_tag_id_list", []),
        }

    def follow_with_profile(self, profile, validated_data):
        id_lists = self.get_id_lists(validated_data)
        profile_id_list = id_lists["profile_id_list"]
        story_location_id_list = id_lists["story_location_id_list"]
        story_tag_id_list = id_lists["story_tag_id_list"]

        if profile_id_list:
            ids_to_follow = Profile.objects.filter(id__in=profile_id_list).values_list(
                "id", flat=True
            )
            profile.followed_authors.add(*ids_to_follow)

        if story_location_id_list:
            ids_to_follow = StoryLocations.objects.filter(
                id__in=story_location_id_list,
            ).values_list(
                "id",
                flat=True,
            )
            profile.followed_locations.add(*ids_to_follow)

        if story_tag_id_list:
            ids_to_follow = StoryTags.objects.filter(
                id__in=story_tag_id_list
            ).values_list("id", flat=True)
            profile.followed_tags.add(*ids_to_follow)

    def unfollow_with_profile(self, profile, validated_data):
        id_lists = self.get_id_lists(validated_data)
        profile_id_list = id_lists["profile_id_list"]
        story_location_id_list = id_lists["story_location_id_list"]
        story_tag_id_list = id_lists["story_tag_id_list"]

        if profile_id_list:
            ids_to_unfollow = Profile.objects.filter(
                id__in=profile_id_list
            ).values_list("id", flat=True)
            profile.followed_authors.remove(*ids_to_unfollow)

        if story_location_id_list:
            ids_to_unfollow = StoryLocations.objects.filter(
                id__in=story_location_id_list
            ).values_list(
                "id",
                flat=True,
            )
            profile.followed_locations.remove(*ids_to_unfollow)

        if story_tag_id_list:
            ids_to_unfollow = StoryTags.objects.filter(
                id__in=story_tag_id_list,
            ).values_list(
                "id",
                flat=True,
            )
            profile.followed_tags.remove(*ids_to_unfollow)


class ReferralSerializer(serializers.Serializer):
    username = serializers.CharField()


class ProfileReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileReferrals
        fields = "__all__"
        extra_kwargs = {
            "accepted": {"required": False},
        }


class RenderProfileSerializer(ProfileReferralSerializer):
    referred_by = TinyProfileSerializer()
    to_profile = TinyProfileSerializer()

    class Meta:
        model = ProfileReferrals
        fields = [
            "id",
            "referred_by",
            "to_profile",
            "accepted",
        ]
