import uuid

from django.db import models

from model_utils.models import TimeStampedModel

# Create your models here.


class AbstractFile(TimeStampedModel):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4)
    data = models.BinaryField()

    class Meta:
        abstract = True


class Picture(AbstractFile):
    pass


class File(AbstractFile):
    pass
