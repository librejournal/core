from django.contrib.postgres.fields import ArrayField
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


class BaseNotification(TimeStampedModel):
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
    followed_id_list = ArrayField(
        models.BigIntegerField(),
        null=True,
        blank=True,
    )

    @property
    def followed_obj_model(self):
        from coreapp.stories.models import Story, Comment, StoryTags, StoryLocations
        from coreapp.users.models import Profile

        types = BaseNotification.NOTIFICATION_TYPES
        return {
            types.STORY_LIKE: Story,
            types.COMMENT_LIKE: Comment,
            types.NEW_STORY_PROFILE: Profile,
            types.NEW_STORY_TAG: StoryTags,
            types.NEW_STORY_LOCATION: StoryLocations,
        }[self.type]

    @property
    def followed_obj_model_name(self):
        return self.followed_obj_model.__name__.upper()

    @property
    def followed_obj_queryset(self):
        return self.followed_obj_model.objects.filter(id__in=self.followed_id_list)



class StoryNotification(models.Model, ModelMessageMixin):
    _message_class = StoryNotificationMessage

    notification = models.OneToOneField(
        "notifications.BaseNotification", on_delete=models.CASCADE
    )
    story = models.ForeignKey(
        "stories.Story", related_name="notifications", on_delete=models.CASCADE
    )


class CommentNotification(models.Model):
    notification = models.OneToOneField(
        "notifications.BaseNotification", on_delete=models.CASCADE
    )
    comment = models.ForeignKey(
        "stories.Comment", related_name="notifications", on_delete=models.CASCADE
    )
