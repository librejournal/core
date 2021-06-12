from django.db import models

from model_utils.models import TimeStampedModel
from model_utils.choices import Choices

# Create your models here.

from coreapp.notifications.processors.message import (
    StoryNotificationMessage,
    BaseNotificationMessage,
)


class ModelMessageMixin:
    _message_class: BaseNotificationMessage = None

    @property
    def message_dict(self):
        return self._message_class(self).to_dict()


class Notification(TimeStampedModel):
    NOTIFICATION_TYPES = Choices(
        "STORY_LIKE",
        "COMMENT_LIKE",
        "NEW_STORY_PROFILE",
        "NEW_STORY_TAG",
        "NEW_STORY_LOCATION",
    )
    type = models.CharField(max_length=50, db_index=True)
    profile = models.ForeignKey(
        "users.Profile", related_name="notifications", on_delete=models.CASCADE
    )
    is_read = models.BooleanField(default=False, db_index=True)


class StoryNotification(Notification, ModelMessageMixin):
    _message_class = StoryNotificationMessage

    story = models.ForeignKey(
        "stories.Story", related_name="notifications", on_delete=models.CASCADE
    )


class CommentNotification(Notification):
    comment = models.ForeignKey(
        "stories.Comment", related_name="notifications", on_delete=models.CASCADE
    )
