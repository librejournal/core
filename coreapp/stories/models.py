import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.functional import cached_property
from model_utils import Choices

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
    is_draft = models.BooleanField(default=True)
    title = models.CharField(max_length=1000, null=True, blank=True)
    thumbnail = models.ForeignKey(
        "files.Picture",
        related_name="stories",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    @cached_property
    def like_count(self):
        return self.likes.filter(is_like=True).count()

    @cached_property
    def dislike_count(self):
        return self.likes.filter(is_like=False).count()

    def profile_has_like_or_dislike(self, profile):
        return self.likes.filter(author=profile).exists()

    def profile_owns_story(self, profile):
        return self.author == profile

    def can_user_like(self, profile):
        # if current story is authored by profile -> False
        if self.profile_owns_story(profile):
            return False
        # (no like / dislike) or (dislike)
        has_dislike = self.likes.filter(author=profile, is_like=False).exists()
        return has_dislike or not self.profile_has_like_or_dislike(profile)

    def can_user_dislike(self, profile):
        # if current story is authored by profile -> False
        if self.profile_owns_story(profile):
            return False
        # (no like / dislike) or (like)
        has_like = self.likes.filter(author=profile, is_like=True).exists()
        return has_like or not self.profile_has_like_or_dislike(profile)

    def like(self, profile):
        kwargs = {
            "story": self,
            "author": profile,
        }
        if not self.profile_has_like_or_dislike(profile):
            self.likes.create(is_like=True, **kwargs)
            return

        dislike = self.likes.filter(is_like=False, **kwargs).first()
        if dislike:
            dislike.is_like = True
            dislike.save()

    def dislike(self, profile):
        kwargs = {
            "story": self,
            "author": profile,
        }
        if not self.profile_has_like_or_dislike(profile):
            self.likes.create(is_like=False, **kwargs)
            return

        like = self.likes.filter(is_like=True, **kwargs).first()
        if like:
            like.is_like = False
            like.save()


class StoryComponent(TimeStampedModel):
    TYPE_CHOICES = Choices(
        "TEXT",
        "TITLE",
        "IMAGE",
    )

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    story = models.ForeignKey(
        Story, on_delete=models.CASCADE, related_name="components"
    )
    picture = models.ForeignKey(
        "files.Picture",
        on_delete=models.CASCADE,
        related_name="components",
        null=True,
        blank=True,
    )
    text = models.TextField()
    # type = TEXT / TITLE / IMAGE - CharField(Enum)
    type = models.CharField(
        max_length=100, choices=TYPE_CHOICES, db_index=True, null=True, blank=True
    )
    # type_setting = CharField
    type_setting = models.CharField(max_length=100, null=True, blank=True)
    order_id = models.IntegerField(null=True, blank=True)

    def _get_order_id(self):
        # if null, just move to last
        parent_story_component_count = self.story.components.count() - (
            1 if self.pk else 0
        )
        return parent_story_component_count + 1

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields", [])
        if not self.order_id:
            self.order_id = self._get_order_id()
            if update_fields:
                update_fields.append("order_id")
                kwargs["update_fields"] = update_fields
        super().save(*args, **kwargs)


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

    @property
    def representation(self):
        return f"StoryTag(id={self.id}, tag={self.tag}, created_by_id={self.created_by_id})"

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

    @property
    def representation(self):
        return "StoryLocations(id=%s, country=%s, city=%s, province_1=%s, province_2=%s, created_by_id=%s)" % (
            self.id,
            self.country,
            self.city,
            self.province_1,
            self.province_2,
            self.created_by_id,
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

    @cached_property
    def like_count(self):
        return self.likes.filter(is_like=True).count()

    @cached_property
    def dislike_count(self):
        return self.likes.filter(is_like=False).count()

    def profile_has_like_or_dislike(self, profile):
        return self.likes.filter(author=profile).exists()

    def profile_owns_story(self, profile):
        return self.author == profile

    def can_user_like(self, profile):
        # if current story is authored by profile -> False
        if self.profile_owns_story(profile):
            return False
        # (no like / dislike) or (dislike)
        has_dislike = self.likes.filter(author=profile, is_like=False).exists()
        return has_dislike or not self.profile_has_like_or_dislike(profile)

    def can_user_dislike(self, profile):
        # if current story is authored by profile -> False
        if self.profile_owns_story(profile):
            return False
        # (no like / dislike) or (like)
        has_like = self.likes.filter(author=profile, is_like=True).exists()
        return has_like or not self.profile_has_like_or_dislike(profile)

    def like(self, profile):
        kwargs = {
            "comment": self,
            "author": profile,
        }
        if not self.profile_has_like_or_dislike(profile):
            self.likes.create(is_like=True, **kwargs)
            return

        dislike = self.likes.filter(is_like=False, **kwargs).first()
        if dislike:
            dislike.is_like = True
            dislike.save()

    def dislike(self, profile):
        kwargs = {
            "comment": self,
            "author": profile,
        }
        if not self.profile_has_like_or_dislike(profile):
            self.likes.create(is_like=False, **kwargs)
            return

        like = self.likes.filter(is_like=True, **kwargs).first()
        if like:
            like.is_like = False
            like.save()


class StoryLikes(TimeStampedModel):
    is_like = models.BooleanField(default=True, db_index=True)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="likes")
    author = models.ForeignKey(
        "users.Profile", on_delete=models.CASCADE, related_name="story_likes"
    )

    def _update_profile_stats(self):
        profile = self.author
        score = profile.weighted_profile_score
        profile_stats = profile.profilestatistics
        profile_stats.reputation = score
        profile_stats.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._update_profile_stats()


class CommentLikes(TimeStampedModel):
    is_like = models.BooleanField(default=True, db_index=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")
    author = models.ForeignKey(
        "users.Profile", on_delete=models.CASCADE, related_name="comment_likes"
    )

    def _update_profile_stats(self):
        profile = self.author
        score = profile.weighted_profile_score
        profile_stats = profile.profilestatistics
        profile_stats.reputation = score
        profile_stats.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._update_profile_stats()
