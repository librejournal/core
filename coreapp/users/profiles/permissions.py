from django.conf import settings

from rest_framework.permissions import BasePermission


class HasReferralsLeft(BasePermission):
    def has_permission(self, request, view):
        referral_count = view.profile.referrers.count()
        return referral_count < settings.MAX_REFERRALS_COUNT
