from rest_framework.permissions import BasePermission


class CanLikeObject(BasePermission):
    # view needs to inherit from LikeDislikeMixin
    def has_permission(self, request, view):
        return view.view_object.can_user_like(view.profile)


class CanDislikeObject(BasePermission):
    # view needs to inherit from LikeDislikeMixin
    def has_permission(self, request, view):
        return view.view_object.can_user_dislike(view.profile)


class DetailViewActionObjectBelongsToProfile(BasePermission):
    def has_permission(self, request, view):
        url_id = view.kwargs.get(view.lookup_url_kwarg, None)
        if not url_id:
            # just pass, this is not a detail action.
            return True
        obj = view.get_object()
        request_profile = getattr(request.user, "profile", None)
        return obj.profile == request_profile
