from django_filters import rest_framework as filters
from django_filters import OrderingFilter, CharFilter

from coreapp.users.models import Profile


class ProfileFilter(filters.FilterSet):
    username = CharFilter(field_name="user__username", lookup_expr="contains")

    class Meta:
        model = Profile
        fields = ["created"]
