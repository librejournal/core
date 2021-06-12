from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView

from coreapp.notifications.serializers import (
    StoryNofiticationSerializer,
    CommentNotificationSerializer,
    BulkReadUnreadActionSerializer,
)
from coreapp.stories.view_mixins import RequestUserProfileMixin
from coreapp.utils.pagination import CustomLimitOffsetPagination


class BaseNotificationViewSet(ModelViewSet, RequestUserProfileMixin):
    authentication_classes = [IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination
    lookup_field = "id"
    lookup_url_kwarg = "id"

    @property
    def view_model(self):
        return self.serializer_class.Meta.model

    def get_query(self):
        status = self.request.query_params.get("status", None)
        base_query = Q(notification_ptr__profile=self.profile)
        if status and status in {"read", "unread"}:
            if status == "read":
                base_query = base_query & Q(notification_ptr__is_read=True)
            if status == "unread":
                base_query = base_query & Q(notification_ptr__is_read=False)
        return base_query

    def get_queryset(self):
        assert self.view_model is not None
        return self.view_model.objects.filter(self.get_query())


class StoryNotificationViewSet(BaseNotificationViewSet):
    serializer_class = StoryNofiticationSerializer


class CommentNotificationViewSet(BaseNotificationViewSet):
    serializer_class = CommentNotificationSerializer


class BulkReadUnreadActionView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BulkReadUnreadActionSerializer

    def _read(self, id_list):
        from coreapp.notifications.models import Notification

        to_update = []
        qs = Notification.objects.filter(id__in=id_list)
        for notification in qs.iterator():
            qs.is_read = True
            to_update.append(notification)
        Notification.objects.bulk_update(to_update, ["is_read"])

    def _unread(self, id_list):
        from coreapp.notifications.models import Notification

        to_update = []
        qs = Notification.objects.filter(id__in=id_list)
        for notification in qs.iterator():
            qs.is_read = False
            to_update.append(notification)
        Notification.objects.bulk_update(to_update, ["is_read"])

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.data["action"]
        id_list = serializer.data["id_list"]
        processor = getattr(self, f"_{action}", None)
        processor(id_list)
        return Response(status=status.HTTP_200_OK)
