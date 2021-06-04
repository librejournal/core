from django.contrib import admin
from django.contrib.auth import get_user_model

# Register your models here.

from coreapp.stories import models as story_models

User = get_user_model()


class StoryLocationAdmin(admin.ModelAdmin):
    model = story_models.StoryLocations
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
    model = story_models.StoryTags
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


class StoryComponentInline(admin.TabularInline):
    model = story_models.StoryComponent
    readonly_fields = ["uuid"]


class StoryTagM2MInline(admin.TabularInline):
    model = story_models.Story.tags.through
    fields = [
        "storytags",
        "representation",
    ]
    readonly_fields = [
        "representation",
    ]

    def representation(self, obj):
        return obj.storytags.representation

    representation.short_description = "Story Tag Representation"


class StoryLocationM2MInline(admin.TabularInline):
    model = story_models.Story.locations.through
    fields = [
        "storylocations",
        "representation",
    ]
    readonly_fields = [
        "representation",
    ]

    def representation(self, obj):
        return obj.storylocations.representation

    representation.short_description = "Story Tag Representation"


class StoryAdmin(admin.ModelAdmin):
    model = story_models.Story
    inlines = [
        StoryComponentInline,
        StoryTagM2MInline,
        StoryLocationM2MInline,
    ]
    fields = [
        "uuid",
        "author",
        "is_draft",
    ]
    readonly_fields = [
        "uuid",
    ]


admin.site.register(story_models.Story, StoryAdmin)
admin.site.register(story_models.StoryLocations, StoryLocationAdmin)
admin.site.register(story_models.StoryTags, StoryTagAdmin)
