from django.urls import path

from rest_framework import routers

from coreapp.users.views import (
    AuthViewSet,
    LoggedInUserViewSet,
    VerificationView,
)
from coreapp.users.profiles.views import ProfileView
from coreapp.users.profiles.urls import urlpatterns as profile_urlpatterns

router = routers.DefaultRouter(trailing_slash=False)
router.register("api/auth", AuthViewSet, basename="auth")
router.register("api/profile", ProfileView, basename="userprofile")

logged_in_user_detail = LoggedInUserViewSet.as_view({"get": "retrieve"})

logged_in_urls = [
    path("api/auth/user", logged_in_user_detail, name="api-rest-logged-in-user-detail"),
    path(
        "api/auth/verification",
        VerificationView.as_view(),
        name="api-rest-verification-view",
    ),
]

urlpatterns = router.urls + logged_in_urls + profile_urlpatterns
