import uuid

from django.contrib.auth import get_user_model
from django.db import models

from model_utils.models import TimeStampedModel

User = get_user_model()

# Create your models here.
class Story(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    author = models.ForeignKey("users.Profile", on_delete=models.CASCADE, related_name="stories")
    tags = models.ManyToManyField("stories.StoryTags")
    locations = models.ManyToManyField("stories.StoryLocations")
    like = models.IntegerField(default=0)
    dislike = models.IntegerField(default=0)


class StoryComponent(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    story = models.ForeignKey(
        Story, on_delete=models.CASCADE, related_name="components"
    )
    text = models.TextField()


class StoryComponentPictures(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    story_component = models.ForeignKey(
        "stories.StoryComponent", on_delete=models.CASCADE, related_name="pictures"
    )
    picture = models.ForeignKey(
        "files.Picture", on_delete=models.CASCADE, related_name="related_picture_components"
    )


class StoryComponentFiles(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    story_component = models.ForeignKey(
        "stories.StoryComponent", on_delete=models.CASCADE, related_name="files"
    )
    file = models.ForeignKey(
        "files.File", on_delete=models.CASCADE, related_name="related_file_components"
    )


class StoryTags(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    tag = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tags")


class StoryLocations(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    province_1 = models.CharField(max_length=50, null=True, blank=True)
    province_2 = models.CharField(max_length=50, null=True, blank=True)


class Comment(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    # Sanitize HTML when saving
    text = models.TextField()
    like = models.IntegerField(default=0)
    dislike = models.IntegerField(default=0)
