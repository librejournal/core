import uuid

from django.db import models

from model_utils.models import TimeStampedModel

# Create your models here.


class AbstractFile(TimeStampedModel):
    attachment_uuid = models.UUIDField(unique=True, default=uuid.uuid4)

    class Meta:
        abstract = True


class Picture(AbstractFile):
    pass


class File(AbstractFile):
    pass
