from django.urls import path, include

from coreapp.users.views import (
    LoggedInUserViewSet,
    VerificationView,
    LoginView,
    LogoutView,
    RegisterView, PasswordResetView,
)
from coreapp.users.profiles import views as profile_views
from coreapp.users.profiles.urls import urlpatterns as profile_urlpatterns

# router = routers.DefaultRouter(trailing_slash=False)
# router.register("api/profile", ProfileView, basename="userprofile")

logged_in_user_detail = LoggedInUserViewSet.as_view(
    {"get": "retrieve"}
)  # added to api spec doc

profile_referals_list_create = profile_views.ProfileReferralsViewSet.as_view(
    {
        "get": "list",
        "post": "create",
    }
)

profile_referals_detail = profile_views.ProfileReferralsViewSet.as_view(
    {
        "get": "retrieve",
        "delete": "destroy",
    }
)

auth_urls = [
    path(
        "api/auth/",
        include(
            [
                path("login", LoginView.as_view(), name="login-view"),
                path("logout", LogoutView.as_view(), name="logout-view"),
                path("register", RegisterView.as_view(), name="register-view"),
                path("password-reset", PasswordResetView.as_view(), name="password-reset"),
            ]
        ),
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
    path("follow", profile_views.FollowView.as_view(), name="follow-action-view"), # added to api spec
    path("unfollow", profile_views.UnfollowView.as_view(), name="follow-action-view"), # added to api spec
    path(
        "self-detail", profile_views.SelfProfileView.as_view(), name="self-profile-view" # added to api spec
    ),
    path("followers", profile_views.ProfileFollowersListView.as_view(), name="self-followers-view"),
    path("following", profile_views.ProfileFollowingListView.as_view(), name="self-following-view"),
]

profile_detail_urls = [
    path(
        "detail", profile_views.ProfileWithPkView.as_view(), name="profile-with-pk-view"
    ),
]

base_referral_urls = [
    path("", profile_referals_list_create, name="referrals-list-create"),
    path(
        "accept",
        profile_views.AcceptWriterInviteView.as_view(),
        name="writer-invite-accept-view",
    ),
]

referral_detail_urls = [
    path("", profile_referals_detail, name="referrals-detail"),
]

profiles_urls = [
    path(
        "api/profiles/",
        include(
            [
                *base_profiles_urls,
                path(
                    "<int:pk>/",
                    include(
                        profile_detail_urls,
                    ),
                ),
                path(
                    "referrals/",
                    include(
                        [
                            path(
                                "<int:pk>/",
                                include(
                                    referral_detail_urls,
                                ),
                            ),
                            *base_referral_urls,
                        ]
                    ),
                ),
            ]
        ),
    )
]

urlpatterns = logged_in_urls + profile_urlpatterns + profiles_urls + auth_urls
