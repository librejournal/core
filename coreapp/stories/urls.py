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

story_component_list_create = views.StoryComponentViewSet.as_view({
    "post": "create",
    "get": "list",
})

story_component_detail = views.StoryComponentViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

urlpatterns = [
    path(
        "api/stories/",
        include(
            [
                path("tags", story_tag_list_create, name="story-tag-list-create"),
                path("locations", story_tag_list_create, name="story-tag-list-create"),
                path("", story_list_create, name="story-list-create"),
                path("drafts", views.ListDraftStories.as_view(), name="list-draft-stories-view"),
                path(
                    "<int:story_id>/",
                    include(
                        [
                            path("", story_detail, name="story-detail"),
                            path("publish", views.PublishStoryView.as_view(), name="publish-story-view"),
                            path(
                                "components/",
                                include(
                                    [
                                        path("", story_component_list_create, name="story-components-list-create"),
                                        path("<int:id>", story_component_detail, name="story-component-detail"),
                                    ]
                                )
                            ),
                        ]
                    )
                ),
            ]
        ),
    )
]
