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
    }
)

urlpatterns = [
    path(
        "api/stories/",
        include(
            [
                path("tags", story_tag_list_create, name="story-tag-list-create"),
                path("locations", story_tag_list_create, name="story-tag-list-create"),
                path("", story_list_create, name="story-list-create"),
                path("<int:id>", story_detail, name="story-detail"),
            ]
        ),
    )
]
