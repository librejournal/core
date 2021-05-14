from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from coreapp.utils.env_utils import is_local_env

User = get_user_model()


class Command(BaseCommand):
    help = "Create initial superuser."

    def handle(self, *args, **options):
        if not is_local_env():
            return
        user, _ = User.objects.get_or_create(username="superuser")
        user.set_password("123123")
        user.is_staff = True
        user.is_superuser = True
        user.save()
