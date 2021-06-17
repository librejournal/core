from rest_framework import serializers

from coreapp.notifications.models import (
    StoryNotification,
    CommentNotification,
    BaseNotification,
)


class BaseNotificationSerializer(serializers.ModelSerializer):
    followed_model_name = serializers.SerializerMethodField()

    class Meta:
        model = BaseNotification
        fields = [
            "id",
            "created",
            "modified",
            "type",
            "is_read",
            "followed_id_list",
            "followed_model_name",
        ]

    def get_followed_model_name(self, obj):
        return obj.followed_obj_model_name


class StoryNofiticationSerializer(serializers.ModelSerializer):
    notification = BaseNotificationSerializer(read_only=True)
    message = serializers.SerializerMethodField()

    class Meta:
        model = StoryNotification
        fields = [
            "notification",
            "story",
            "message",
        ]

    def get_message(self, obj):
        return getattr(obj, "message_dict", {})


class CommentNotificationSerializer(serializers.ModelSerializer):
    notification = BaseNotificationSerializer(read_only=True)
    message = serializers.SerializerMethodField()

    class Meta:
        model = CommentNotification
        fields = [
            "notification",
            "comment",
            "message",
        ]

    def get_message(self, obj):
        return getattr(obj, "message_dict", {})


class BulkReadUnreadActionSerializer(serializers.SerializerMethodField):
    id_list = serializers.ListField(child=serializers.IntegerField())
    action = serializers.ChoiceField(choices=["read", "unread"])
