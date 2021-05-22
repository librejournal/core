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

stories_root_urls_list = [
    # api/stories/
    path("tags", story_tag_list_create, name="story-tag-list-create"),
    path("locations", story_tag_list_create, name="story-tag-list-create"),
    path("", story_list_create, name="story-list-create"),  # added to api spec doc
    path(
        "drafts",
        views.ListDraftStories.as_view(),
        name="list-draft-stories-view",
    ),
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

story_detail_urls_list = [
    # api/stories/<int:story_id>/
    path("", story_detail, name="story-detail"),  # added to api spec doc
    path(
        "publish",
        views.PublishStoryView.as_view(),
        name="publish-story-view",
    ),  # added to api spec doc
    *components_urls_list,
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