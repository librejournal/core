import copy

from django.utils.functional import cached_property
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from coreapp.stories import serializers as story_serializers
from coreapp.stories import models as story_models
from coreapp.stories.view_mixins import StoryMixin, LikeDislikeView, RequestUserProfileMixin


class StoryCommentViewSet(ModelViewSet, StoryMixin):
    serializer_class = story_serializers.StoryCommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    lookup_field = "id"
    lookup_url_kwarg = "id"
    queryset = story_models.Comment.objects.all()

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["story"] = self.story
        ctx["author"] = getattr(self.request.user, "profile", None)
        return ctx


class StoryLocationViewSet(ModelViewSet):
    serializer_class = story_serializers.StoryLocationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    lookup_field = "id"
    lookup_url_kwarg = "id"
    queryset = story_models.StoryLocations.objects.all()


class StoryTagViewSet(ModelViewSet):
    serializer_class = story_serializers.StoryTagsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    lookup_field = "id"
    lookup_url_kwarg = "id"
    queryset = story_models.StoryTags.objects.all()


class StoryViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    # Implement pagination class
    pagination_class = None
    lookup_field = "id"
    lookup_url_kwarg = "story_id"
    queryset = story_models.Story.objects.filter(is_draft=False)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return story_serializers.RenderStorySerializer
        return story_serializers.StorySerializer

    def get_permission_classes(self):
        if self.request.method == "GET":
            return [AllowAny]
        return [IsAuthenticated]

    def get_permissions(self):
        return [permission() for permission in self.get_permission_classes()]


class DraftStoryViewSet(StoryViewSet, RequestUserProfileMixin):
    lookup_url_kwarg = "draft_story_id"

    def get_queryset(self):
        request_user_profile = self.profile
        assert request_user_profile is not None
        return story_models.Story.objects.filter(
            author=request_user_profile,
            is_draft=True,
        )


class StoryComponentViewSet(ModelViewSet, StoryMixin):
    serializer_class = story_serializers.StoryComponentSerializer
    permission_classes = [IsAuthenticated]
    # Implement pagination class
    pagination_class = None
    lookup_field = "id"
    lookup_url_kwarg = "id"

    def get_serializer_class(self):
        if self.request.method == "GET":
            return story_serializers.StoryComponentRenderSerializer
        return story_serializers.StoryComponentSerializer

    def get_queryset(self):
        assert self.story_id is not None
        return story_models.StoryComponent.objects.filter(
            story_id=self.story_id,
        )

    def create(self, request, *args, **kwargs):
        request_data = copy.deepcopy(request.data)
        request_data["story"] = self.story_id
        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class UpdateStoryComponentOrderView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = story_serializers.StoryComponentOrderSerializer

    def _bulk_update_order_ids(self):
        bulk_update_list = []
        for component in self.get_queryset().iterator():
            component.order_id = self.id_to_order_id_map[component.id]
            bulk_update_list.append(component)
        updated_qs = story_models.StoryComponent.objects.bulk_update(
            bulk_update_list,
            ["order_id"],
        )
        return updated_qs

    @cached_property
    def request_data(self):
        serializer = story_serializers.StoryComponentOrderSerializer(
            data=self.request.data, many=True
        )
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    @cached_property
    def id_to_order_id_map(self):
        mapping = {}
        for data in self.request_data:
            mapping[data["id"]] = data["order_id"]
        return mapping

    @cached_property
    def story_component_id_list(self):
        return list(self.id_to_order_id_map.keys())

    def get_queryset(self):
        return story_models.StoryComponent.objects.filter(
            id__in=self.story_component_id_list,
        )

    def post(self, request, *args, **kwargs):
        self._bulk_update_order_ids()
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class PublishStoryView(GenericAPIView, StoryMixin):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        assert self.story_id is not None
        story = story_models.Story.objects.get(id=self.story_id)
        story.is_draft = False
        story.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListDraftStories(ListAPIView, RequestUserProfileMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = story_serializers.RenderStorySerializer

    def get_queryset(self):
        request_user_profile = self.profile
        assert request_user_profile is not None
        return story_models.Story.objects.filter(
            author=request_user_profile,
            is_draft=True,
        )

class StoryLikeView(LikeDislikeView):
    action_type = "like"
    object_type = "story"

class StoryDislikeView(LikeDislikeView):
    action_type = "dislike"
    object_type = "story"

class CommentLikeView(LikeDislikeView):
    action_type = "like"
    object_type = "comment"

class CommentDislikeView(LikeDislikeView):
    action_type = "dislike"
    object_type = "comment"
