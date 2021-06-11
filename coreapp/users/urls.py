from django.urls import path, include

from rest_framework import routers

from coreapp.users.views import (
    LoggedInUserViewSet,
    VerificationView,
    LoginView,
    LogoutView,
    RegisterView,
)
from coreapp.users.profiles import views as profile_views
from coreapp.users.profiles.views import ProfileView
from coreapp.users.profiles.urls import urlpatterns as profile_urlpatterns

router = routers.DefaultRouter(trailing_slash=False)
router.register("api/profile", ProfileView, basename="userprofile")

logged_in_user_detail = LoggedInUserViewSet.as_view(
    {"get": "retrieve"}
)  # added to api spec doc

auth_urls = [
    path(
        "api/auth",
        include(
            [
                path("/login", LoginView.as_view(), name="login-view"),
                path("/logout", LogoutView.as_view(), name="logout-view"),
                path("/register", RegisterView.as_view(), name="register-view"),
            ]
        )
    )
]

logged_in_urls = [
    path("api/auth/user", logged_in_user_detail, name="api-rest-logged-in-user-detail"),
    path(
        "api/auth/verification",
        VerificationView.as_view(),
        name="api-rest-verification-view",
    ),
]

base_profiles_urls = [
    path("/follow", profile_views.FollowView.as_view(), name="follow-action-view"),
    path("/unfollow", profile_views.UnfollowView.as_view(), name="follow-action-view"),
    path("/self-detail", profile_views.SelfProfileView.as_view(), name="self-profile-view"),
]

profile_detail_urls = [
    path("/detail", profile_views.ProfileWithPkView.as_view(), name="profile-with-pk-view"),
]

profiles_urls = [
    path(
        "api/profiles",
        include(
            [
                *base_profiles_urls,
                path(
                    "/<int:pk>",
                    include(
                        profile_detail_urls,
                    )
                )
            ]
        ),
    )
]

urlpatterns = router.urls + logged_in_urls + profile_urlpatterns + profiles_urls
