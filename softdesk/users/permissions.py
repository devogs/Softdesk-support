# softdesk/users/permissions.py
from rest_framework import permissions


class IsUserOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object (the user themselves)
    or admin users to view, edit, or delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, OPTIONS requests for authenticated users (to view their own profile)
        # Admins can view any profile
        if request.method in permissions.SAFE_METHODS:
            return obj == request.user or request.user.is_staff or request.user.is_superuser

        # For PUT, PATCH, DELETE requests, object must be the user themselves or the user must be an admin
        return obj == request.user or request.user.is_staff or request.user.is_superuser