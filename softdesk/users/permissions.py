# softdesk/users/permissions.py
from rest_framework import permissions


class IsUserOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object (the user themselves)
    or admin users to view, edit, or delete it.
    """

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return obj == request.user or request.user.is_staff or request.user.is_superuser

        return obj == request.user or request.user.is_staff or request.user.is_superuser
