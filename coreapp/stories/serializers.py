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


class StoryComponentSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(choices=models.StoryComponent.TYPE_CHOICES)
    type_setting = serializers.CharField(required=True)

    class Meta:
        model = models.StoryComponent
        fields = [
            "id",
            "order_id",
            "story",
            "text",
            "type",
            "type_setting",
        ]
        read_only_fields = [
            "id",
            "order_id",
        ]


class StoryComponentOrderSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    order_id = serializers.IntegerField()


class StorySerializer(serializers.ModelSerializer):
    # creation and update only...
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

    can_user_like = serializers.SerializerMethodField()
    can_user_dislike = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(read_only=True, default=0)
    dislike_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = models.Story
        fields = [
            "id",
            "uuid",
            "created",
            "modified",
            "is_draft",
            "author",
            "tags",
            "locations",
            "components",
            "can_user_like",
            "can_user_dislike",
            "like_count",
            "dislike_count",
        ]
        read_only_fields = [
            "id",
            "uuid",
            "created",
            "modified",
            "can_user_like",
            "can_user_dislike",
            "like_count",
            "dislike_count",
        ]

    @property
    def request_user_profile(self):
        request_user = getattr(get_current_request(), "user", None)
        return getattr(request_user, "profile", None)

    def get_can_user_like(self, obj):
        if isinstance(obj, dict):
            return False
        return obj.can_user_like(self.request_user_profile)

    def get_can_user_dislike(self, obj):
        if isinstance(obj, dict):
            return False
        return obj.can_user_dislike(self.request_user_profile)


class RenderStorySerializer(serializers.ModelSerializer):
    # for retrieve / list actions
    author = serializers.SerializerMethodField()
    tags = StoryTagsSerializer(read_only=True, many=True)
    locations = StoryLocationSerializer(read_only=True, many=True)
    components = StoryComponentSerializer(read_only=True, many=True)
    can_user_like = serializers.SerializerMethodField()
    can_user_dislike = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(read_only=True, default=0)
    dislike_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = models.Story
        fields = [
            "id",
            "uuid",
            "created",
            "modified",
            "is_draft",
            "author",
            "tags",
            "locations",
            "components",
            "can_user_like",
            "can_user_dislike",
            "like_count",
            "dislike_count",
        ]

    @property
    def request_user_profile(self):
        request_user = getattr(get_current_request(), "user", None)
        return getattr(request_user, "profile", None)

    @property
    def is_public_user(self):
        is_authenticated = getattr(
            getattr(
                get_current_request(),
                "user",
                None,
            ),
            "is_authenticated",
            False,
        )
        return not is_authenticated

    def get_author(self, obj):
        from coreapp.users.profiles.serializers import TinyProfileSerializer

        return TinyProfileSerializer(obj.author).data

    def get_can_user_like(self, obj):
        if isinstance(obj, dict) or self.is_public_user:
            return False
        return obj.can_user_like(self.request_user_profile)

    def get_can_user_dislike(self, obj):
        if isinstance(obj, dict) or self.is_public_user:
            return False
        return obj.can_user_dislike(self.request_user_profile)

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     for idx, component in enumerate(data["components"]):
    #         component["order_id"] = idx + 1
    #     return data

    def save(self, **kwargs):
        raise NotImplementedError(
            "This serializer shouldn't be used for modifying Story!"
        )
