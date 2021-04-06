from django.db import models

from model_utils.models import TimeStampedModel

# Create your models here.


class AbstractFile(TimeStampedModel):
    attachment_uuid = models.UUIDField()

    class Meta:
        abstract = True


class Picture(AbstractFile, TimeStampedModel):
    pass


class File(AbstractFile, TimeStampedModel):
    pass
