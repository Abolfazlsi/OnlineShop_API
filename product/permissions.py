from rest_framework import permissions
from cart.models import Order


# check user is owner or not
class IsCommentOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class IsOrderOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        return obj.user == request.user
