import os

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from coreapp.utils.env_utils import is_local_env

User = get_user_model()


class Command(BaseCommand):
    help = "Create initial superuser."

    def handle(self, *args, **options):
        user, _ = User.objects.get_or_create(username="superuser")
        user.set_password(os.environ.get("SU_PWD"))
        user.is_staff = True
        user.is_superuser = True
        user.save()
