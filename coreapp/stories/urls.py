from django.urls import path, include


from coreapp.stories import views

story_location_list_create = views.StoryLocationViewSet.as_view(
    {
        "get": "list",
        "post": "create",
    }
)

story_tag_list_create = views.StoryTagViewSet.as_view(
    {
        "get": "list",
        "post": "create",
    }
)

story_list_create = views.StoryViewSet.as_view(
    {
        "get": "list",
        "post": "create",
    }
)

story_detail = views.StoryViewSet.as_view(
    {
        "get": "retrieve",
        "patch": "partial_update",
        "put": "update",
        "delete": "destroy",
    }
)

story_component_list_create = views.StoryComponentViewSet.as_view(
    {
        "post": "create",
        "get": "list",
    }
)

story_component_detail = views.StoryComponentViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)

comments_list_create = views.StoryCommentViewSet.as_view(
    {
        "post": "create",
        "get": "list",
    }
)

comments_detail = views.StoryCommentViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)

draft_story_list = views.DraftStoryViewSet.as_view(
    {
        "get": "list",
    }
)

draft_story_detail = views.DraftStoryViewSet.as_view(
    {
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
        "get": "retrieve",
    }
)

draft_story_urls = [
    # api/stories/drafts
    path(
        "drafts/",
        include(
            [
                path(
                    "",
                    draft_story_list,
                    name="draft-story-list",
                ),
                path(
                    "<int:draft_story_id>",
                    draft_story_detail,
                    name="draft-story-detail",
                ),
            ]
        ),
    )
]

stories_root_urls_list = [
    # api/stories/
    path("tags", story_tag_list_create, name="story-tag-list-create"),
    path("locations", story_location_list_create, name="story-tag-list-create"),
    path("", story_list_create, name="story-list-create"),  # added to api spec doc
    *draft_story_urls,
]

components_urls_list = [
    # api/stories/<int:story_id>/
    path(
        "components/",
        include(
            [
                path(
                    "",
                    story_component_list_create,
                    name="story-components-list-create",
                ),  # added to api spec doc
                path(
                    "<int:id>",
                    story_component_detail,
                    name="story-component-detail",
                ),  # added to api spec doc
                path(
                    "order",
                    views.UpdateStoryComponentOrderView.as_view(),
                    name="story-component-update-order",
                ),  # added to api spec doc
            ]
        ),
    )
]

comments_urls_list = [
    # api/stories/<int:story_id>/
    path(
        "comments/",
        include(
            [
                path(
                    "",
                    comments_list_create,
                    name="story-comments-list-create",
                ),
                path(
                    "<int:id>/",
                    include(
                        [
                            path(
                                "",
                                comments_detail,
                                name="story-comments-detail",
                            ),
                            path(
                                "like",
                                views.CommentLikeView.as_view(),
                                name="story-comments-like",
                            ),
                            path(
                                "dislike",
                                views.CommentDislikeView.as_view(),
                                name="story-comments-like",
                            ),
                        ]
                    ),
                ),
            ]
        ),
    )
]

story_detail_urls_list = [
    # api/stories/<int:story_id>/
    path("", story_detail, name="story-detail"),  # added to api spec doc
    path(
        "publish",
        views.PublishStoryView.as_view(),
        name="publish-story-view",
    ),  # added to api spec doc
    path(
        "like",
        views.StoryLikeView.as_view(),
        name="story-like-view",
    ),
    path(
        "dislike",
        views.StoryDislikeView.as_view(),
        name="story-like-view",
    ),
    *components_urls_list,
    *comments_urls_list,
]

urlpatterns = [
    path(
        "api/stories/",
        include(
            [
                *stories_root_urls_list,
                path(
                    "<int:story_id>/",
                    include(
                        story_detail_urls_list,
                    ),
                ),
            ]
        ),
    )
]
