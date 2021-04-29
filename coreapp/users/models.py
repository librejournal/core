import uuid
import logging

from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings

from model_utils.models import TimeStampedModel
from model_utils.choices import Choices

from rest_framework.authtoken.models import Token


TOKEN_TYPE_CHOICES = Choices(
    'GENERIC',
    'EMAIL_VERIFICATION',
    'SMS_VERIFICATION',
)
PROFILE_TYPE_CHOICES = Choices(
    'WRITER',
    'READER',
)

logger = logging.getLogger(__name__)

def _get_default_valid_until(*args, **kwargs):
    return timezone.now() + timedelta(days=1)

class User(AbstractUser, TimeStampedModel):
    # ForeignKey to self...
    # enum CharField( READER / WRITER )
    uuid = models.UUIDField(unique=True, default=uuid.uuid4)

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
    user = models.ForeignKey(User, related_name="generic_tokens", on_delete=models.CASCADE)
    key = models.CharField(max_length=40, primary_key=True)
    type = models.CharField(choices=TOKEN_TYPE_CHOICES, max_length=100, default=TOKEN_TYPE_CHOICES.GENERIC)
    valid_until = models.DateTimeField(default=_get_default_valid_until)

    class Meta:
        unique_together = [['user', 'type']]

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
    uuid = models.UUIDField(unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, choices=PROFILE_TYPE_CHOICES, default=PROFILE_TYPE_CHOICES.READER)
    followed_locations = models.ManyToManyField(
        "stories.StoryLocations",
        related_name="followed_by",
    )
    followed_authors = models.ManyToManyField("self", related_name="followed_by")

class UserVerification(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_verified = models.DateTimeField()
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
        token = self.user.get_or_create_verification_token(TOKEN_TYPE_CHOICES.EMAIL_VERIFICATION)
        send_simple_verification_mail(self.user.email, str(token.key))

    def _send_verification_sms(self):
        if not settings.ENABLE_SMS:
            logger.debug("SMSs are not enabled.")
            return
        token_key = self.user.get_or_create_verification_token(TOKEN_TYPE_CHOICES.SMS_VERIFICATION)

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


class UserStatisticts(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reputation = models.IntegerField()
    number_of_posts = models.IntegerField()
