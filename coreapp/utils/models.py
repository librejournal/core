import uuid

from django.db import models


class AbstractUUIDModel:
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)

    class Meta:
        abstract = True
