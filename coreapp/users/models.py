from django.contrib.auth.models import AbstractUser
from django.db import models

from model_utils.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    # ForeignKey to self...
    # enum CharField( READER / WRITER )
    type = models.CharField(max_length=50)
    followed_locations = models.ManyToManyField(
        "stories.StoryLocations",
    )
    followed_authors = models.ManyToManyField("users.User")


class UserVerification(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_verified = models.DateTimeField()
    # SMS verif?
    sms_verified = models.DateTimeField()


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
