from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "coreapp.users"

    def ready(self):
        from .models import User, Profile, PROFILE_TYPE_CHOICES

        user = User.get_system_user()
        Profile.objects.get_or_create(
            user=user,
            type=PROFILE_TYPE_CHOICES.WRITER,
        )
