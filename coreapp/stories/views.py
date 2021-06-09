import copy

from django.contrib.postgres.aggregates import StringAgg
from django.db.models import F, Subquery, OuterRef, Count, Value
from django.db.models.functions import Concat
from django.utils.functional import cached_property
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from coreapp.stories import serializers as story_serializers
from coreapp.stories import models as story_models
from coreapp.stories.view_mixins import (
    StoryMixin,
    LikeDislikeView,
    RequestUserProfileMixin,
)
from coreapp.stories.filters import StoryFilter, CommentFilter, TagFilter, LocationFilter
from coreapp.utils.pagination import CustomLimitOffsetPagination


class StoryCommentViewSet(ModelViewSet, StoryMixin):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination
    lookup_field = "id"
    lookup_url_kwarg = "id"

    filterset_class = CommentFilter
    filter_backends = (filters.DjangoFilterBackend,)

    def get_queryset(self):
        return story_models.Comment.objects.filter(story_id=self.story_id,).annotate(
            profile_score=F("author__profilestatistics__reputation"),
            likes_count=Subquery(
                story_models.CommentLikes.objects.filter(
                    is_like=True,
                    comment=OuterRef("pk"),
                )
                .values(
                    "comment",
                )
                .annotate(
                    count=Count("pk"),
                )
                .values(
                    "count",
                )
            ),
            dislikes_count=Subquery(
                story_models.CommentLikes.objects.filter(
                    is_like=False,
                    comment=OuterRef("pk"),
                )
                .values(
                    "comment",
                )
                .annotate(
                    count=Count("pk"),
                )
                .values(
                    "count",
                )
            ),
        )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return story_serializers.StoryCommentRenderSerializer
        return story_serializers.StoryCommentSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["story"] = self.story
        ctx["author"] = getattr(self.request.user, "profile", None)
        return ctx


class StoryLocationViewSet(ModelViewSet):
    serializer_class = story_serializers.StoryLocationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination
    lookup_field = "id"
    lookup_url_kwarg = "id"

    filterset_class = LocationFilter
    filter_backends = (filters.DjangoFilterBackend,)

    def get_queryset(self):
        qs = story_models.StoryLocations.objects.all()
        return qs.annotate(
            location_search=Concat(
                F("country"),
                Value("^"),
                F("city"),
                Value("^"),
                F("province_1"),
                Value("^"),
                F("province_2"),
            ),
        )


class StoryTagViewSet(ModelViewSet):
    serializer_class = story_serializers.StoryTagsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination
    lookup_field = "id"
    lookup_url_kwarg = "id"
    queryset = story_models.StoryTags.objects.all()

    filterset_class = TagFilter
    filter_backends = (filters.DjangoFilterBackend,)


class StoryViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    # Implement pagination class
    pagination_class = CustomLimitOffsetPagination
    lookup_field = "id"
    lookup_url_kwarg = "story_id"

    filterset_class = StoryFilter
    filter_backends = (filters.DjangoFilterBackend,)

    @property
    def story_qs(self):
        return story_models.Story.objects.all()

    @property
    def non_draft_story_qs(self):
        return self.story_qs.filter(is_draft=False)

    def annotate_search_fields(self, qs):
        if self.request.query_params.get("locations", ""):
            qs = qs.annotate(
                location_search=Concat(
                    StringAgg("locations__country", delimiter="^", distinct=True),
                    StringAgg("locations__city", delimiter="^", distinct=True),
                    StringAgg("locations__province_1", delimiter="^", distinct=True),
                    StringAgg("locations__province_2", delimiter="^", distinct=True),
                ),
            )

        if self.request.query_params.get("tags", ""):
            qs = qs.annotate(
                tag_search=StringAgg("tags__tag", delimiter="^", distinct=True),
            )

        return qs

    def annotate_profile_score(self, qs):
        return qs.annotate(
            profile_score=F("author__profilestatistics__reputation"),
        )

    def annotate_likes_count(self, qs):
        return qs.annotate(
            likes_count=Subquery(
                story_models.StoryLikes.objects.filter(
                    is_like=True,
                    story=OuterRef("pk"),
                ).values(
                    "story",
                ).annotate(
                    count=Count("pk"),
                ).values(
                    "count",
                )
            ),
        )

    def annotate_dislikes_count(self, qs):
        return qs.annotate(
            dislikes_count=Subquery(
                story_models.StoryLikes.objects.filter(
                    is_like=False,
                    story=OuterRef("pk"),
                ).values(
                    "story",
                ).annotate(
                    count=Count("pk"),
                ).values(
                    "count",
                )
            ),
        )

    def annotate_ordering_fields(self, qs):
        ordering_param_value = list(
            reversed(self.request.query_params.get("ordering", "").split("-"))
        )[0]
        if not ordering_param_value:
            return qs

        if ordering_param_value == "score":
            qs = self.annotate_profile_score(qs)

        if ordering_param_value == "likes":
            qs = self.annotate_likes_count(qs)

        if ordering_param_value == "dislikes":
            qs = self.annotate_dislikes_count(qs)

        return qs

    def get_queryset(self):
        qs = self.annotate_search_fields(self.non_draft_story_qs)
        return self.annotate_ordering_fields(qs)

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

class MyStoriesViewSet(StoryViewSet, RequestUserProfileMixin):
    def get_permission_classes(self):
        return [IsAuthenticated]

    def get_queryset(self):
        qs = self.story_qs.filter(
            author=self.profile,
        )
        return self.annotate_ordering_fields(qs)


class StoryComponentViewSet(ModelViewSet, StoryMixin):
    serializer_class = story_serializers.StoryComponentSerializer
    permission_classes = [IsAuthenticated]
    # Implement pagination class
    pagination_class = CustomLimitOffsetPagination
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
