from coreapp.stories.models import Story, Comment
from coreapp.users.models import Profile
from coreapp.notifications.models import (
    BaseNotification,
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
    reverse_relation_name = None

    def __init__(self, *args, **kwargs):
        self.relation_pk = kwargs.pop("relation_pk", None)
        self.args = args
        self.kwargs = kwargs

    def get_affected_queryset(self):
        return []

    def get_followed_obj_id_list(self):
        return []

    @property
    def relation_name(self):
        return self.relation_name

    @property
    def relation_obj(self):
        return self.relation_model.objects.filter(pk=self.relation_pk).first()

    def post_base_notification_action(self, base_notification):
        return

    def post_notification_action(self, notification):
        return

    def process(self):
        relation_name, relation_obj = self.relation_name, self.relation_obj
        for obj in self.get_affected_queryset():
            get_or_create_kwargs = {
                "type": self.notification_type,
                "profile": obj,
                self.reverse_relation_name: relation_obj,
                "defaults": {
                    "followed_id_list": self.get_followed_obj_id_list(),
                    "is_read": False,
                },
            }
            base_notification, _ = BaseNotification.objects.update_or_create(
                **get_or_create_kwargs,
            )
            self.post_base_notification_action(base_notification)
            creation_kwargs = {
                relation_name: relation_obj,
                "notification": base_notification,
            }
            notification, _ = self.notification_model.objects.get_or_create(
                **creation_kwargs
            )
            self.post_notification_action(notification)


class NewStoryByAuthorProcessor(GenericNotificationProcessor):
    notification_model = StoryNotification
    notification_type = BaseNotification.NOTIFICATION_TYPES.NEW_STORY_PROFILE
    relation_model = Story
    relation_name = "story"
    reverse_relation_name = "storynotification__story"

    def get_affected_queryset(self):
        return profile_queryset_following_author(self.relation_pk)

    def get_followed_obj_id_list(self):
        return [self.relation_obj.author.id]


class NewStoryByTagProcessor(GenericNotificationProcessor):
    notification_model = StoryNotification
    notification_type = BaseNotification.NOTIFICATION_TYPES.NEW_STORY_TAG
    relation_model = Story
    relation_name = "story"
    reverse_relation_name = "storynotification__story"

    def get_affected_queryset(self):
        return profile_queryset_following_tags(self.relation_pk)

    def get_followed_obj_id_list(self):
        return list(self.relation_obj.tags.values_list("id", flat=True))


class NewStoryByLocationProcessor(GenericNotificationProcessor):
    notification_model = StoryNotification
    notification_type = BaseNotification.NOTIFICATION_TYPES.NEW_STORY_LOCATION
    relation_model = Story
    relation_name = "story"
    reverse_relation_name = "storynotification__story"

    def get_affected_queryset(self):
        return profile_queryset_following_locations(self.relation_pk)

    def get_followed_obj_id_list(self):
        return list(self.relation_obj.locations.values_list("id", flat=True))


class StoryLikeProcessor(GenericNotificationProcessor):
    notification_model = StoryNotification
    notification_type = BaseNotification.NOTIFICATION_TYPES.STORY_LIKE
    relation_model = Story
    relation_name = "story"
    reverse_relation_name = "storynotification__story"

    def get_affected_queryset(self):
        story = Story.objects.get(id=self.relation_pk)
        return [story.author]

    def get_followed_obj_id_list(self):
        return [self.relation_obj.id]


class CommentLikeProcessor(GenericNotificationProcessor):
    notification_model = CommentNotification
    notification_type = BaseNotification.NOTIFICATION_TYPES.COMMENT_LIKE
    relation_model = Comment
    relation_name = "comment"
    reverse_relation_name = "commentnotification__comment"

    def get_affected_queryset(self):
        comment = Comment.objects.get(id=self.relation_pk)
        return [comment.author]

    def get_followed_obj_id_list(self):
        return [self.relation_obj.id]
