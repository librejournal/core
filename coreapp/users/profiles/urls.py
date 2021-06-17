from django.urls import path

from coreapp.users.profiles.views import TinyProfileViewSet

list_profiles = TinyProfileViewSet.as_view({"get": "list"})

# profile_router = routers.DefaultRouter(trailing_slash=False)
# profile_router.register("api/user/profile", ProfileView, basename="user-profile")

user_profile_urls = [path("api/user/profiles", list_profiles, name="list-profiles")]

urlpatterns = user_profile_urls
