from django.db import models

from model_utils.models import TimeStampedModel
from model_utils.choices import Choices

# Create your models here.

class Notification(TimeStampedModel):
    NOTIFICATION_TYPES = Choices(
        "STORY_LIKE",
        "COMMENT_LIKE",
        "NEW_STORY_PROFILE",
        "NEW_STORY_TAG",
        'NEW_STORY_LOCATION',
    )
    type = models.CharField(max_length=50, db_index=True)
    profile = models.ForeignKey("users.Profile", related_name="notifications", on_delete=models.CASCADE)

class StoryNotification(Notification):
    story = models.ForeignKey("stories.Story", related_name="notifications", on_delete=models.CASCADE)

class CommentNotification(Notification):
    comment = models.ForeignKey("stories.Comment", related_name="notifications", on_delete=models.CASCADE)
