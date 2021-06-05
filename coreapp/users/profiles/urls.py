from django.urls import path

from rest_framework import routers

from coreapp.users.profiles.views import ProfileView, TinyProfileViewSet

list_profiles = TinyProfileViewSet.as_view({"get": "list"})

profile_router = routers.DefaultRouter(trailing_slash=False)
profile_router.register("api/user/profile", ProfileView, basename="user-profile")

profile_urls = [
    path("api/user/profiles", list_profiles, name="list-profiles")
]

urlpatterns = profile_urls + profile_router.urls
