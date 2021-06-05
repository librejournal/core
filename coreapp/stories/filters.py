from django_filters import rest_framework as filters
from django_filters import OrderingFilter, BaseInFilter

from coreapp.stories.models import Story

class StoryFilter(filters.FilterSet):
    ordering = OrderingFilter(
        fields=(
            ("created", "date"),
            ("profile_score", "score"),
            ("likes_count", "likes"),
            ("dislikes_count", "dislikes"),
        )
    )

    class Meta:
        model = Story
        fields = "__all__"
