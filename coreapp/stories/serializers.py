from django.contrib.auth import get_user_model

from rest_framework import serializers

from coreapp.stories import models
from coreapp.files.models import Picture
from coreapp.users.models import (
    Profile,
)

from coreapp.utils.global_request import get_current_request
from coreapp.files.serializers import PictureSerializer

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
        extra_kwargs = {
            "city": {"required": False},
            "province_1": {"required": False},
            "province_2": {"required": False},
        }

    def to_internal_value(self, data):
        internal = super().to_internal_value(data)
        internal["created_by"] = _get_current_user_or_system_user_profile()
        return internal


class StoryComponentSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(choices=models.StoryComponent.TYPE_CHOICES)
    type_setting = serializers.CharField(required=True)
    picture = serializers.PrimaryKeyRelatedField(
        queryset=Picture.objects.all(),
        required=False,
    )

    class Meta:
        model = models.StoryComponent
        fields = [
            "id",
            "order_id",
            "story",
            "text",
            "picture",
            "type",
            "type_setting",
        ]
        read_only_fields = [
            "id",
            "order_id",
        ]


class StoryComponentRenderSerializer(StoryComponentSerializer):
    picture = PictureSerializer(read_only=True)

    class Meta(StoryComponentSerializer.Meta):
        pass


class StoryComponentOrderSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    order_id = serializers.IntegerField()


class StoryCommentSerializer(serializers.ModelSerializer):
    can_user_like = serializers.SerializerMethodField()
    can_user_dislike = serializers.SerializerMethodField()
    like_count = serializers.IntegerField(read_only=True, default=0)
    dislike_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = models.Comment
        fields = [
            "id",
            "uuid",
            "created",
            "story",
            "author",
            "text",
            "can_user_like",
            "can_user_dislike",
            "like_count",
            "dislike_count",
        ]
        extra_kwargs = {
            "created": {"read_only": True},
            "story": {"required": False},
            "author": {"required": False},
        }

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        data["story"] = self.context["story"]
        data["author"] = self.context["author"]
        return data

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


class StoryCommentRenderSerializer(StoryCommentSerializer):
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        from coreapp.users.profiles.serializers import TinyProfileSerializer

        serializer = TinyProfileSerializer(obj.author)
        return serializer.data

    class Meta(StoryCommentSerializer.Meta):
        pass


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
    thumbnail = serializers.PrimaryKeyRelatedField(
        queryset=Picture.objects.all(),
        required=False,
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
            "thumbnail",
            "title",
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
    components = StoryComponentRenderSerializer(read_only=True, many=True)
    thumbnail = PictureSerializer(read_only=True)
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
            "thumbnail",
            "title",
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

        profile_score = getattr(obj, "profile_score", None)
        return TinyProfileSerializer(
            obj.author, context={"profile_score": profile_score}
        ).data

    def get_can_user_like(self, obj):
        if isinstance(obj, dict) or self.is_public_user:
            return False
        return obj.can_user_like(self.request_user_profile)

    def get_can_user_dislike(self, obj):
        if isinstance(obj, dict) or self.is_public_user:
            return False
        return obj.can_user_dislike(self.request_user_profile)

    def save(self, **kwargs):
        raise NotImplementedError(
            "This serializer shouldn't be used for modifying Story!"
        )


class LikeDislikeSerializer(serializers.Serializer):
    story_id = serializers.IntegerField(required=False)
    comment_id = serializers.IntegerField(required=False)

    def get_ids(self):
        return {
            "story_id": getattr(self.context.get("story", None), "id", None),
            "comment_id": getattr(self.context.get("comment", None), "id", None),
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        ids = self.get_ids()
        if ids["story_id"] and ids["comment_id"]:
            raise serializers.ValidationError(
                "Shouldn't recieve both story_id and comment_id."
            )
        attrs.update(ids)
        return attrs

    def like(self, profile, validated_data):
        story_id = validated_data["story_id"]
        comment_id = validated_data["comment_id"]

        if story_id:
            story = models.Story.objects.get(id=story_id)
            story.like(profile)

        if comment_id:
            comment = models.Comment.objects.get(id=comment_id)
            comment.like(profile)

    def dislike(self, profile, validated_data):
        story_id = validated_data["story_id"]
        comment_id = validated_data["comment_id"]

        if story_id:
            story = models.Story.objects.get(id=story_id)
            story.dislike(profile)

        if comment_id:
            comment = models.Comment.objects.get(id=comment_id)
            comment.dislike(profile)
