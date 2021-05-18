import logging

from django.conf import settings
from django.apps import AppConfig
from django.db import OperationalError, ProgrammingError

from coreapp.utils.env_utils import is_local_env

logger = logging.getLogger(__name__)

class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "coreapp.users"

    def _create_system_user(self):
        from .models import User, Profile, PROFILE_TYPE_CHOICES

        user = User.get_system_user()
        Profile.objects.get_or_create(
            user=user,
            type=PROFILE_TYPE_CHOICES.WRITER,
        )

    def _create_service_users_and_tokens(self):
        from rest_framework.authtoken.models import Token
        from .models import User

        current_service = "core"
        for key, value in settings.SERVICES.items():
            if key == current_service or not key:
                continue

            user, _ = User.objects.get_or_create(username=key)
            user.set_unusable_password()
            user.save()

            access_token = value['access_token'] or Token.generate_key()
            try:
                token = Token.objects.get(user_id=user.id)
            except Token.DoesNotExist:
                Token.objects.create(user_id=user.id, key=access_token)
            else:
                token = Token.objects.filter(user_id=user.id).update(key=access_token)

    def _create_superuser(self):
        from .models import User
        if not is_local_env():
            return
        user, _ = User.objects.get_or_create(username="superuser")
        user.set_password("123123")
        user.is_staff = True
        user.is_superuser = True
        user.save()

    def ready(self):
        try:
            self._create_system_user()
            self._create_service_users_and_tokens()
            self._create_superuser()
        except (OperationalError, ProgrammingError):
            logger.debug("System user and tokens are not created because tables don't exist...")
