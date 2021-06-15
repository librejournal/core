from rest_framework.permissions import BasePermission

from coreapp.users.models import UserVerification


class IsUserNotVerifiedYet(BasePermission):
    def has_permission(self, request, view):
        user_verification = UserVerification.objects.filter(
            user=request.user,
        ).first()

        if not user_verification:
            return True
        return not user_verification.is_verified


class IsUserVerified(BasePermission):
    def has_permission(self, request, view):
        return not IsUserNotVerifiedYet().has_permission(request, view)
