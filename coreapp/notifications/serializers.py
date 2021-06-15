from rest_framework import serializers

from coreapp.notifications.models import StoryNotification, CommentNotification


class BaseNotificationSerializerMixin:
    id = serializers.IntegerField(source="notification.id", read_only=True)
    created = serializers.DateTimeField(source="notification.created", read_only=True)
    modified = serializers.DateTimeField(source="notification.modified", read_only=True)
    type = serializers.CharField(source="notification.type", read_only=True)
    is_read = serializers.CharField(source="notification.is_read", read_only=True)
    message = serializers.SerializerMethodField()
    followed_id_list = serializers.ListField(serializers.IntegerField(), read_only=True)
    followed_model_name = serializers.CharField(
        source="notification.followed_obj_model_name"
    )

    class Meta:
        fields = [
            "id",
            "created",
            "modified",
            "type",
            "message",
            "is_read",
            "followed_id_list",
            "followed_model_name",
        ]

    def get_message(self, obj):
        return obj.message_dict


class StoryNofiticationSerializer(
    serializers.ModelSerializer,
    BaseNotificationSerializerMixin,
):
    class Meta(BaseNotificationSerializerMixin.Meta):
        model = StoryNotification
        fields = BaseNotificationSerializerMixin.Meta.fields + [
            "story",
        ]


class CommentNotificationSerializer(
    serializers.ModelSerializer,
    BaseNotificationSerializerMixin,
):
    class Meta(BaseNotificationSerializerMixin.Meta):
        model = StoryNotification
        fields = BaseNotificationSerializerMixin.Meta.fields + [
            "comment",
        ]


class BulkReadUnreadActionSerializer(serializers.SerializerMethodField):
    id_list = serializers.ListField(child=serializers.IntegerField())
    action = serializers.ChoiceField(choices=["read", "unread"])
