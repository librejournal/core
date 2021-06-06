from django_filters import rest_framework as filters
from django_filters import OrderingFilter, CharFilter

from coreapp.stories.models import Story, Comment, StoryTags, StoryLocations


class StoryFilter(filters.FilterSet):
    ordering = OrderingFilter(
        fields=(
            ("created", "date"),
            ("profile_score", "score"),
            ("likes_count", "likes"),
            ("dislikes_count", "dislikes"),
        )
    )
    components = CharFilter(field_name="components__text", lookup_expr="contains")
    tags = CharFilter(field_name="tag_search", lookup_expr="contains")
    locations = CharFilter(field_name="location_search", lookup_expr="contains")

    class Meta:
        model = Story
        fields = ["created"]


class CommentFilter(filters.FilterSet):
    ordering = OrderingFilter(
        fields=(
            ("created", "date"),
            ("profile_score", "score"),
            ("likes_count", "likes"),
            ("dislikes_count", "dislikes"),
        )
    )

    class Meta:
        model = Comment
        fields = ["created"]

class TagFilter(filters.FilterSet):
    search = CharFilter(field_name="tag", lookup_expr="contains")

    class Meta:
        model = StoryTags
        fields = ["created"]

class LocationFilter(filters.FilterSet):
    search = CharFilter(field_name="location_search", lookup_expr="contains")

    class Meta:
        model = StoryLocations
        fields = ["created"]
