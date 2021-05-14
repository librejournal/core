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
    lookup_url_kwarg = "id"
    queryset = story_models.Story.objects.all()
