import os
import logging

from celery import Celery
from django.conf import settings

logger = logging.getLogger(__name__)

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coreapp.coreapp.settings")
logger.debug(f"Trying to connect CELERY_BROKER_URL: {settings.CELERY_BROKER_URL}")
logger.debug(
    f"Trying to connect CELERY_RESULT_BACKEND: {settings.CELERY_RESULT_BACKEND}"
)

app = Celery("librejournal")

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
