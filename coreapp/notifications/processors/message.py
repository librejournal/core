class BaseNotificationMessage:
    def __init__(self, notification_object):
        self.notification = notification_object

    @property
    def related_obj(self):
        raise NotImplementedError

    @property
    def summary_title(self):
        raise NotImplementedError

    @property
    def summary_text(self):
        raise NotImplementedError

    def to_dict(self):
        return {
            "title": self.summary_title,
            "text": self.summary_text,
            "related_obj_pk": self.related_obj.pk,
            "notification_pk": self.notification.pk,
            "likes": getattr(self.related_obj, "like_count", None),
            "dislikes": getattr(self.related_obj, "dislike_count", None),
        }


class StoryNotificationMessage(BaseNotificationMessage):
    @property
    def related_obj(self):
        return self.notification.story

    @property
    def summary_text(self):
        return f"Story(title: {self.related_obj.title})."

    @property
    def summary_title(self):
        return "A story has been published."

class CommentNotificationMessage(BaseNotificationMessage):
    @property
    def related_obj(self):
        return self.notification.comment

    @property
    def summary_text(self):
        return f"Comment(story_id={self.related_obj.story_id})"

    @property
    def summary_title(self):
        return "Comment like / dislike changed."
