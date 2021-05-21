from django.contrib import admin
from django.contrib.auth import get_user_model

# Register your models here.

from coreapp.stories.models import StoryLocations, StoryTags

User = get_user_model()


class StoryLocationAdmin(admin.ModelAdmin):
    model = StoryLocations
    list_display = [
        "id",
        "uuid",
        "country",
        "city",
    ]
    fields = [
        "id",
        "uuid",
        "country",
        "city",
        "province_1",
        "province_2",
        "created_by",
    ]
    readonly_fields = [
        "id",
        "uuid",
    ]

    def save_model(self, request, obj, form, change):
        # profile for system user...
        sys_profile = User.get_system_user().profile
        obj.created_by = sys_profile
        super().save_model(request, obj, form, change)


class StoryTagAdmin(admin.ModelAdmin):
    model = StoryTags
    list_display = [
        "id",
        "uuid",
        "tag",
    ]
    fields = [
        "id",
        "uuid",
        "tag",
        "created_by",
    ]
    readonly_fields = [
        "id",
        "uuid",
    ]

    def save_model(self, request, obj, form, change):
        # profile for system user...
        sys_profile = User.get_system_user().profile
        obj.created_by = sys_profile
        super().save_model(request, obj, form, change)


admin.site.register(StoryLocations, StoryLocationAdmin)
admin.site.register(StoryTags, StoryTagAdmin)
