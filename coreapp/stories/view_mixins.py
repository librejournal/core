from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT


class RequestUserProfileMixin:
    @property
    def profile_id(self):
        return getattr(self.request.user, "profile_id", None)

    @property
    def profile(self):
        return getattr(self.request.user, "profile", None)


class StoryMixin:
    @property
    def story_id(self):
        return self.kwargs.get("story_id", None)

    @property
    def story(self):
        from coreapp.stories.models import Story

        return Story.objects.filter(id=self.story_id).first()


class LikeDislikeView(GenericAPIView, StoryMixin):
    from coreapp.stories.serializers import LikeDislikeSerializer

    serializer_class = LikeDislikeSerializer
    # like or dislike
    action_type = None
    # story or comment
    object_type = None

    @property
    def profile(self):
        return getattr(self.request.user, "profile", None)

    @property
    def comment_id(self):
        return self.kwargs.get("id", None)

    @property
    def comment(self):
        from coreapp.stories.models import Comment

        return Comment.objects.filter(id=self.comment_id).first()

    @property
    def view_object(self):
        if self.object_type == "story":
            return self.story
        elif self.object_type == "comment":
            return self.comment

    @property
    def dynamic_permission_classes(self):
        from coreapp.stories.permissions import CanLikeObject, CanDislikeObject

        classes = [IsAuthenticated]
        if self.action_type == "like":
            classes.append(CanLikeObject)
        elif self.action_type == "dislike":
            classes.append(CanDislikeObject)
        return classes

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        if self.object_type == "story":
            ctx["story"] = self.story
        elif self.object_type == "comment":
            ctx["comment"] = self.comment
        return ctx

    def get_permissions(self):
        return [permission() for permission in self.dynamic_permission_classes]

    def _like(self):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.like(self.profile, serializer.validated_data)

    def _dislike(self):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.dislike(self.profile, serializer.validated_data)

    def _process(self):
        processor = getattr(self, f"_{self.action_type}", None)
        assert processor is not None
        processor()

    def post(self, request, *args, **kwargs):
        self._process()
        return Response(status=HTTP_204_NO_CONTENT)
