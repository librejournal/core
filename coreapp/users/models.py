import uuid
import logging

from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.utils.functional import cached_property

from model_utils.models import TimeStampedModel
from model_utils.choices import Choices

from rest_framework.authtoken.models import Token


WEEKLY_WEIGHT=3
MONTHLY_WEIGHT=2
REST_WEIGHT=1
WEIGHTS_SUM=sum([WEEKLY_WEIGHT, MONTHLY_WEIGHT, REST_WEIGHT])



TOKEN_TYPE_CHOICES = Choices(
    "GENERIC",
    "EMAIL_VERIFICATION",
    "SMS_VERIFICATION",
)
PROFILE_TYPE_CHOICES = Choices(
    "WRITER",
    "READER",
)

logger = logging.getLogger(__name__)


def _get_default_valid_until(*args, **kwargs):
    return timezone.now() + timedelta(days=1)


def _filter_story_likes_with_profile(profile, **filter_kwargs):
    from coreapp.stories.models import StoryLikes

    return StoryLikes.objects.filter(
        story__author=profile,
        **filter_kwargs,
    )


def _filter_comment_likes_with_profile(profile, **filter_kwargs):
    from coreapp.stories.models import CommentLikes

    return CommentLikes.objects.filter(
        comment__story__author=profile,
        **filter_kwargs,
    )


class User(AbstractUser, TimeStampedModel):
    # ForeignKey to self...
    # enum CharField( READER / WRITER )
    uuid = models.UUIDField(unique=True, default=uuid.uuid4)

    @classmethod
    def get_system_user(cls):
        obj, _ = cls.objects.get_or_create(
            username="librejournal_system",
            defaults={
                "is_staff": True,
                "first_name": "System",
                "last_name": "System",
                "email": "system@librejournal.codes",
            },
        )
        obj.set_unusable_password()
        obj.save()
        return obj

    @property
    def is_verified(self):
        return getattr(getattr(self, "userverification", None), "is_verified", False)

    def get_or_create_verification_token(self, type):
        verif_token = self.generic_tokens.filter(
            type=type,
        ).first()
        if verif_token:
            return verif_token
        return self.generic_tokens.create(type=TOKEN_TYPE_CHOICES.EMAIL_VERIFICATION)

    def verify_user(self, token):
        token = self.get_or_create_verification_token()
        verification = UserVerification.objects.get_or_create(user=self)
        if not verification.is_verified:
            if token.type == TOKEN_TYPE_CHOICES.EMAIL_VERIFICATION:
                verification.email_verified = timezone.now()
                verification.save()
                token.delete()


class GenericToken(TimeStampedModel):
    user = models.ForeignKey(
        User, related_name="generic_tokens", on_delete=models.CASCADE
    )
    key = models.CharField(max_length=40, primary_key=True)
    type = models.CharField(
        choices=TOKEN_TYPE_CHOICES, max_length=100, default=TOKEN_TYPE_CHOICES.GENERIC
    )
    valid_until = models.DateTimeField(default=_get_default_valid_until)

    class Meta:
        unique_together = [["user", "type"]]

    @classmethod
    def generate_key(cls):
        return Token.generate_key()

    @property
    def is_valid_key(self):
        return timezone.now() + self.valid_until

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)


class Profile(TimeStampedModel):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=50, choices=PROFILE_TYPE_CHOICES, default=PROFILE_TYPE_CHOICES.READER
    )
    followed_locations = models.ManyToManyField(
        "stories.StoryLocations",
        related_name="followed_by",
    )
    followed_tags = models.ManyToManyField(
        "stories.StoryTags",
        related_name="followed_by",
    )
    followed_authors = models.ManyToManyField("self", related_name="followed_by")

    @property
    def posts_count(self):
        return self.stories.count()

    @property
    def story_likes_qs(self):
        return _filter_story_likes_with_profile(self)

    @property
    def comment_likes_qs(self):
        return _filter_comment_likes_with_profile(self)

    @property
    def story_likes(self):
        return self.story_likes_qs.count()

    @property
    def comment_likes(self):
        return self.comment_likes_qs.count()

    @cached_property
    def date_range_queries(self):
        now = timezone.now()
        last_week_start_dt = now - relativedelta(weeks=1)
        last_month_start_dt = now - relativedelta(months=1)
        return {
            "last_week": Q(created__gte=last_week_start_dt) & Q(created__lte=now),
            "last_month": Q(created__gte=last_month_start_dt)
            & Q(created__lt=last_week_start_dt),
            "rest": Q(created__lt=last_month_start_dt),
        }

    @property
    def story_likes_in_last_week(self):
        return self.story_likes_qs.filter(self.date_range_queries["last_week"]).count()

    @property
    def comment_likes_in_last_week(self):
        return self.comment_likes_qs.filter(
            self.date_range_queries["last_week"]
        ).count()

    @property
    def story_likes_in_last_month(self):
        return self.story_likes_qs.filter(self.date_range_queries["last_month"]).count()

    @property
    def comment_likes_in_last_month(self):
        return self.comment_likes_qs.filter(
            self.date_range_queries["last_month"]
        ).count()

    @property
    def story_likes_rest(self):
        return self.story_likes_qs.filter(self.date_range_queries["rest"]).count()

    @property
    def comment_likes_rest(self):
        return self.comment_likes_qs.filter(self.date_range_queries["rest"]).count()

    @property
    def weighted_story_likes_average(self):
        return (
            self.story_likes_in_last_week * WEEKLY_WEIGHT
            + self.story_likes_in_last_month * MONTHLY_WEIGHT
            + self.story_likes_rest * REST_WEIGHT
        ) / WEIGHTS_SUM

    @property
    def weighted_comment_likes_average(self):
        return (
            self.comment_likes_in_last_week * WEEKLY_WEIGHT
            + self.comment_likes_in_last_month * MONTHLY_WEIGHT
            + self.comment_likes_rest
        ) / WEIGHTS_SUM

    @property
    def weighted_profile_score(self):
        return (
            self.weighted_story_likes_average * 2 + self.weighted_comment_likes_average
        ) / 3

    def _create_profile_statistics(self):
        stats = getattr(self, "profilestatistics", None)
        if not stats:
            stats, _ = ProfileStatistics.objects.get_or_create(profile=self)
        return stats

    @property
    def profile_statistics(self):
        return self._create_profile_statistics()

    def __str__(self):
        return f"User(username={self.user.username}) Profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._create_profile_statistics()


class UserVerification(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_verified = models.DateTimeField(null=True, blank=True)
    # SMS verif?
    sms_verified = models.DateTimeField(null=True, blank=True)

    @property
    def is_verified(self):
        return bool(self.email_verified)

    def _send_verification_email(self):
        from coreapp.users.verification.email import send_simple_verification_mail

        if not settings.ENABLE_EMAILS:
            logger.debug("Emails are not enabled.")
            return
        token = self.user.get_or_create_verification_token(
            TOKEN_TYPE_CHOICES.EMAIL_VERIFICATION
        )
        send_simple_verification_mail(self.user.email, str(token.key))

    def _send_verification_sms(self):
        if not settings.ENABLE_SMS:
            logger.debug("SMSs are not enabled.")
            return
        token_key = self.user.get_or_create_verification_token(
            TOKEN_TYPE_CHOICES.SMS_VERIFICATION
        )

    def save(self, *args, **kwargs):
        if not self.pk:
            self._send_verification_email()
            self._send_verification_sms()
        super().save(*args, **kwargs)


class UserReferrals(TimeStampedModel):
    token = models.CharField(max_length=200)
    referred_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="referrals"
    )
    to_email = models.EmailField()


class ProfileStatistics(TimeStampedModel):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    reputation = models.FloatField(null=True, blank=True)
    number_of_posts = models.IntegerField(null=True, blank=True)
