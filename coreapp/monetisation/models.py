from django.contrib.auth import get_user_model
from django.db import models

from model_utils.models import TimeStampedModel

User = get_user_model()

# Create your models here.


class Donation(TimeStampedModel):
    amount = models.FloatField()
    donator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="given_donations"
    )
    reciever = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recieved_donations"
    )


class Subscription(TimeStampedModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscribed_to"
    )
    subscribed_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subs"
    )
    begin = models.DateTimeField()


class AdRevenue(TimeStampedModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="revenue")
    amount = models.FloatField()
    billing_date = models.DateTimeField()
