from django.contrib.auth import get_user_model

from rest_framework import serializers

from coreapp.stories import models
from coreapp.users.models import (
    Profile,
)

from coreapp.utils.global_request import get_current_request

User = get_user_model()


def _get_current_user_or_system_user():
    user = getattr(get_current_request(), "user", None)
    if not user or not user.is_authenticated:
        return User.get_system_user()
    return user


def _get_current_user_or_system_user_profile():
    user = _get_current_user_or_system_user()
    return getattr(user, "profile", None)


class StoryTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StoryTags
        fields = "__all__"

    def to_internal_value(self, data):
        internal = super().to_internal_value(data)
        internal["created_by"] = _get_current_user_or_system_user_profile()
        return internal


class StoryLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StoryLocations
        fields = "__all__"

    def to_internal_value(self, data):
        internal = super().to_internal_value(data)
        internal["created_by"] = _get_current_user_or_system_user_profile()
        return internal


class StorySerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())
    tags = serializers.PrimaryKeyRelatedField(
        queryset=models.StoryTags.objects.all(),
        required=False,
        many=True,
    )
    locations = serializers.PrimaryKeyRelatedField(
        queryset=models.StoryLocations.objects.all(),
        required=False,
        many=True,
    )
    components = serializers.PrimaryKeyRelatedField(
        queryset=models.StoryComponent.objects.all(),
        required=False,
        many=True,
    )

    class Meta:
        model = models.Story
        fields = [
            "id",
            "uuid",
            "author",
            "tags",
            "locations",
            "components",
        ]

    can_user_like = serializers.SerializerMethodField()
    can_user_dislike = serializers.SerializerMethodField()

    def get_can_user_like(self, obj):
        if isinstance(obj, dict):
            return False
        request_user = getattr(get_current_request(), "user", None)
        return obj.can_user_like(request_user)

    def get_can_user_dislike(self, obj):
        if isinstance(obj, dict):
            return False
        request_user = getattr(get_current_request(), "user", None)
        return obj.can_user_dislike(request_user)
