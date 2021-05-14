import copy

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

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
    serializer_class = story_serializers.StorySerializer
    permission_classes = [IsAuthenticated]
    # Implement pagination class
    pagination_class = None
    lookup_field = "id"
    lookup_url_kwarg = "story_id"
    queryset = story_models.Story.objects.all()


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
        story_id = self.kwargs.get("story_id", None)
        return story_models.Story.objects.filter(id=story_id).first()

    def get_queryset(self):
        assert self.story_id is not None
        return story_models.StoryComponent.objects.filter(
            story_id=self.story_id,
        )

    def create(self, request, *args, **kwargs):
        request_data = copy.deepcopy(request.data)
        request_data['story'] = self.story_id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
