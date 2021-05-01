from django.urls import path

from rest_framework import routers

from coreapp.users.profiles.views import ProfileView

profile_router = routers.DefaultRouter(trailing_slash=False)
profile_router.register("api/user/profile", ProfileView, basename="user-profile")

profile_urls = []

urlpatterns = profile_urls + profile_router.urls
