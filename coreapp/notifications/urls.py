from django.urls import path, include

from coreapp.notifications import views as notification_views

story_notification_list = notification_views.StoryNotificationViewSet.as_view(
    {
        "get": "list",
    }
)

comment_notification_list = notification_views.CommentNotificationViewSet.as_view(
    {
        "get": "list",
    }
)

story_notification_urls = [
    path("", story_notification_list, name="story-notifications-list"),
]

comment_notification_urls = [
    path("", comment_notification_list, name="comment-notifications-list"),
]

urlpatterns = [
    path(
        "api/notifications/",
        include(
            [
                path(
                    "bulk-mark-as",
                    notification_views.BulkReadUnreadActionView.as_view(),
                    name="bulk-mark-as-view",
                ),
                path(
                    "stories/",
                    include(
                        [
                            *story_notification_urls
                        ]
                    )
                ),
                path(
                    "comments/",
                    include(
                        [
                            *comment_notification_urls,
                        ]
                    )
                )
            ]
        )
    )
]