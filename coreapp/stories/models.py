import uuid

from django.contrib.auth import get_user_model
from django.db import models

from model_utils.models import TimeStampedModel

User = get_user_model()

# Create your models here.
class Story(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    author = models.ForeignKey(
        "users.Profile", on_delete=models.CASCADE, related_name="stories"
    )
    tags = models.ManyToManyField("stories.StoryTags")
    locations = models.ManyToManyField("stories.StoryLocations")

    def profile_has_like_or_dislike(self, profile):
        return self.likes.filter(author=profile).exists()

    def can_user_like(self, profile):
        # (no like / dislike) or (dislike)
        has_dislike = self.likes.filter(author=profile, is_like=False).exists()
        return has_dislike or not self.user_has_like_or_dislike(profile)

    def can_user_dislike(self, profile):
        # (no like / dislike) or (like)
        has_like = self.likes.filter(author=profile, is_like=True).exists()
        return has_like or not self.user_has_like_or_dislike(profile)

    def like(self, profile):
        kwargs = {
            "story": self,
            "author": profile,
        }
        if not self.user_has_like_or_dislike(profile):
            self.likes.create(is_like=True, **kwargs)

        dislike = self.likes.filter(is_like=False, **kwargs).first()
        if dislike:
            dislike.is_like = True
            dislike.save()

    def dislike(self, profile):
        kwargs = {
            "story": self,
            "author": profile,
        }
        if not self.user_has_like_or_dislike(profile):
            self.likes.create(is_like=False, **kwargs)

        like = self.likes.filter(is_like=True, **kwargs).first()
        if like:
            like.is_like = False
            like.save()


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
        "files.Picture",
        on_delete=models.CASCADE,
        related_name="related_picture_components",
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
    created_by = models.ForeignKey(
        "users.Profile",
        on_delete=models.CASCADE,
        related_name="tags",
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.created_by:
            system_profile = User.get_system_user().profile
            self.created_by = system_profile

            update_fields = kwargs.get("update_fields", None)
            if update_fields:
                kwargs["update_fields"] = set(update_fields).union({"created_by"})

        return super().save(*args, **kwargs)


class StoryLocations(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    province_1 = models.CharField(max_length=50, null=True, blank=True)
    province_2 = models.CharField(max_length=50, null=True, blank=True)
    created_by = models.ForeignKey(
        "users.Profile",
        on_delete=models.CASCADE,
        related_name="locations",
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.created_by:
            system_profile = User.get_system_user().profile
            self.created_by = system_profile

            update_fields = kwargs.get("update_fields", None)
            if update_fields:
                kwargs["update_fields"] = set(update_fields).union({"created_by"})

        return super().save(*args, **kwargs)


class Comment(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        "users.Profile", on_delete=models.CASCADE, related_name="comments"
    )
    # Sanitize HTML when saving
    text = models.TextField()


class StoryLikes(TimeStampedModel):
    is_like = models.BooleanField(default=True)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="likes")
    author = models.ForeignKey(
        "users.Profile", on_delete=models.CASCADE, related_name="story_likes"
    )


class CommentLikes(TimeStampedModel):
    is_like = models.BooleanField(default=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")
    author = models.ForeignKey(
        "users.Profile", on_delete=models.CASCADE, related_name="comment_likes"
    )
