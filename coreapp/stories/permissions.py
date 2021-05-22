from rest_framework.permissions import BasePermission

class CanLikeObject(BasePermission):
    # view needs to inherit from LikeDislikeMixin
    def has_permission(self, request, view):
        return view.view_object.can_user_like(view.profile)

class CanDislikeObject(BasePermission):
    # view needs to inherit from LikeDislikeMixin
    def has_permission(self, request, view):
        return view.view_object.can_user_dislike(view.profile)
