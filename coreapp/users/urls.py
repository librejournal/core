from django.urls import path

from rest_framework import routers

from coreapp.users.views import AuthViewSet, LoggedInUserViewSet, VerificationView

router = routers.DefaultRouter(trailing_slash=False)
router.register("api/auth", AuthViewSet, basename="auth")

logged_in_user_detail = LoggedInUserViewSet.as_view({"get": "retrieve"})

logged_in_urls = [
    path("api/auth/user", logged_in_user_detail, name="api-rest-logged-in-user-detail"),
    path("api/auth/verification", VerificationView.as_view(), name="api-rest-verification-view"),
]

urlpatterns = router.urls + logged_in_urls
