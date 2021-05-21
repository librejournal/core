import copy

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from coreapp.stories import serializers as story_serializers
from coreapp.stories import models as story_models


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
        return [
            permission() for permission in self.get_permission_classes()
        ]



class StoryComponentViewSet(ModelViewSet):
    serializer_class = story_serializers.StoryComponentSerializer
    permission_classes = [IsAuthenticated]
    # Implement pagination class
    pagination_class = None
    lookup_field = "id"
    lookup_url_kwarg = "id"

    @property
    def story_id(self):
        return self.kwargs.get("story_id", None)

    @property
    def story(self):
        return story_models.Story.objects.filter(id=self.story_id).first()

    def get_queryset(self):
        assert self.story_id is not None
        return story_models.StoryComponent.objects.filter(
            story_id=self.story_id,
        )

    def create(self, request, *args, **kwargs):
        request_data = copy.deepcopy(request.data)
        request_data['story'] = self.story_id
        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PublishStoryView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @property
    def story_id(self):
        return self.kwargs.get("story_id", None)

    def post(self, request, *args, **kwargs):
        assert self.story_id is not None
        story = story_models.Story.objects.get(id=self.story_id)
        story.is_draft = False
        story.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ListDraftStories(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = story_serializers.RenderStorySerializer

    def get_queryset(self):
        request_user_profile = getattr(self.request.user, "profile", None)
        assert request_user_profile is not None
        return story_models.Story.objects.filter(
            author=request_user_profile,
            is_draft=True,
        )
