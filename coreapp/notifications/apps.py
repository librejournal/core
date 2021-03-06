from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "coreapp.notifications"

    def ready(self):
        try:
            import coreapp.notifications.tasks
        except ImportError:
            pass
