from django.db.models.signals import post_save
from django.dispatch import receiver

from coreapp.stories.models import Story

# @receiver(post_save, sender=Story)
# def post_save_story_notifications(sender, instance, **kwargs):
#     from coreapp.notifications.tasks import run_new_story_notifications_processor_task
#     if not instance.is_draft:
#         run_new_story_notifications_processor_task.delay(instance.id)
