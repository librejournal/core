from rest_framework import serializers

from coreapp.notifications.models import StoryNotification, CommentNotification

class BaseNotificationSerializerMixin:
    id = serializers.IntegerField(source="notification_ptr.id", read_only=True)
    created = serializers.DateTimeField(source="notification_ptr.created", read_only=True)
    modified = serializers.DateTimeField(source="notification_ptr.modified", read_only=True)
    type = serializers.CharField(source="notification_ptr.type", read_only=True)
    is_read = serializers.CharField(source="notification_ptr.is_read", read_only=True)
    message = serializers.SerializerMethodField()

    class Meta:
        fields = [
            "id",
            "created",
            "modified",
            "type",
            "message",
            "is_read",
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
