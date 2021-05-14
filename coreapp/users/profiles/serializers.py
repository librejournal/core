from django.contrib.auth import get_user_model

from rest_framework import serializers

from coreapp.users.models import Profile, PROFILE_TYPE_CHOICES
from coreapp.users.serializers import UserSerializer, TinyUserSerializer
from coreapp.stories.models import StoryLocations
from coreapp.stories.serializers import StoryLocationSerializer

User = get_user_model()


class TinyProfileSerializer(serializers.ModelSerializer):
    user = TinyUserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            "uuid",
            "type",
            "user",
        ]


class ProfileSerializer(serializers.ModelSerializer):
    followed_authors = TinyProfileSerializer(many=True, read_only=True)
    followed_locations = StoryLocationSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            "uuid",
            "type",
            "user",
            "followed_locations",
            "followed_authors",
        ]


class FollowUnfollowSerializer(serializers.Serializer):
    profile_uuid_list = serializers.ListField(child=serializers.UUIDField())
    story_location_uuid_list = serializers.ListField(child=serializers.UUIDField())

    def follow_with_profile(self, profile, validated_data):
        profile_uuid_list = validated_data["profile_uuid_list"]
        story_location_uuid_list = validated_data["story_location_uuid_list"]

        if profile_uuid_list:
            profiles_to_follow = Profile.objects.filter(uuid__in=profile_uuid_list)
            profile.followed_authors.add(*profiles_to_follow)

        if story_location_uuid_list:
            locations_to_follow = StoryLocations.objects.filter(
                uuid__in=story_location_uuid_list
            )
            profile.followed_locations.add(*locations_to_follow)

    def unfollow_with_profile(self, profile, validated_data):
        profile_uuid_list = validated_data["profile_uuid_list"]
        story_location_uuid_list = validated_data["story_location_uuid_list"]

        if profile_uuid_list:
            profiles_to_follow = Profile.objects.filter(uuid__in=profile_uuid_list)
            profile.followed_authors.remove(*profiles_to_follow)

        if story_location_uuid_list:
            locations_to_follow = StoryLocations.objects.filter(
                uuid__in=story_location_uuid_list
            )
            profile.followed_locations.remove(*locations_to_follow)
