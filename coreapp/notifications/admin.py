from django.contrib import admin
from coreapp.notifications.models import (
    BaseNotification,
    CommentNotification,
    StoryNotification,
)

# Register your models here.
class BaseNotificationInline(admin.TabularInline):
    model = BaseNotification


class CommentNotificationAdmin(admin.ModelAdmin):
    model = CommentNotification
    inlines = [
        BaseNotificationInline,
    ]


class StoryNotificationAdmin(admin.ModelAdmin):
    model = StoryNotification
    inlines = [
        BaseNotificationInline,
    ]


admin.site.register(CommentNotification, CommentNotificationAdmin)
admin.site.register(StoryNotification, StoryNotificationAdmin)
