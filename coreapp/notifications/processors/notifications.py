from coreapp.stories.models import Story, Comment
from coreapp.users.models import Profile
from coreapp.notifications.models import (
    Notification,
    StoryNotification,
    CommentNotification,
)


def profile_queryset_following_tags(story_id):
    story = Story.objects.get(id=story_id)
    story_tags = story.tags.all()
    return Profile.objects.filter(
        followed_tags__in=story_tags,
    )


def profile_queryset_following_locations(story_id):
    story = Story.objects.get(id=story_id)
    story_locations = story.locations.all()
    return Profile.objects.filter(
        followed_locations__in=story_locations,
    )


def profile_queryset_following_author(story_id):
    story = Story.objects.get(id=story_id)
    return Profile.objects.filter(
        followed_authors__in=[story.author],
    )


class GenericNotificationProcessor:
    notification_type = None
    notification_model = None
    relation_model = None
    relation_name = None

    def __init__(self, *args, **kwargs):
        self.relation_pk = kwargs.pop("relation_pk", None)
        self.args = args
        self.kwargs = kwargs

    def get_notificaion_relation(self):
        obj = self.relation_model.objects.filter(pk=self.relation_pk).first()
        return self.relation_name, obj

    def get_affected_queryset(self):
        return []

    def process(self):
        relation_name, relation_obj = self.get_notificaion_relation()
        for obj in self.get_affected_queryset():
            base_notification = Notification.objects.create(
                type=self.notification_type,
                profile=obj,
            )
            creation_kwargs = {
                relation_name: relation_obj,
                "notification_ptr": base_notification,
            }
            self.notification_model.objects.get_or_create(**creation_kwargs)


class NewStoryByAuthorProcessor(GenericNotificationProcessor):
    notification_model = StoryNotification
    notification_type = Notification.NOTIFICATION_TYPES.NEW_STORY_PROFILE
    relation_model = Story
    relation_name = "story"

    def get_affected_queryset(self):
        return profile_queryset_following_author(self.relation_pk)


class NewStoryByTagProcessor(GenericNotificationProcessor):
    notification_model = StoryNotification
    notification_type = Notification.NOTIFICATION_TYPES.NEW_STORY_TAG
    relation_model = Story
    relation_name = "story"

    def get_affected_queryset(self):
        return profile_queryset_following_tags(self.relation_pk)


class NewStoryByLocationProcessor(GenericNotificationProcessor):
    notification_model = StoryNotification
    notification_type = Notification.NOTIFICATION_TYPES.NEW_STORY_LOCATION
    relation_model = Story
    relation_name = "story"

    def get_affected_queryset(self):
        return profile_queryset_following_locations(self.relation_pk)


class StoryLikeProcessor(GenericNotificationProcessor):
    notification_model = StoryNotification
    notification_type = Notification.NOTIFICATION_TYPES.STORY_LIKE
    relation_model = Story
    relation_name = "story"

    def get_affected_queryset(self):
        story = Story.objects.get(id=self.relation_pk)
        return [story.author]


class CommentLikeProcessor(GenericNotificationProcessor):
    notification_model = CommentNotification
    notification_type = Notification.NOTIFICATION_TYPES.COMMENT_LIKE
    relation_model = Comment
    relation_name = "comment"

    def get_affected_queryset(self):
        story = Story.objects.get(id=self.relation_pk)
        return [story.author]
