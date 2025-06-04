# issues/permissions.py
from rest_framework import permissions

from projects.models import Project
from .models import Issue, Comment


class IsProjectContributor(permissions.BasePermission):
    """
    Custom permission to only allow contributors of a project to access its issues/comments.
    """

    def has_permission(self, request, view):
        """
        Checks if the user is an authenticated contributor to the project.

        This permission is used for list views of issues/comments
        and for creating new issues/comments within a project.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Get project_pk from URL kwargs
        project_pk = view.kwargs.get("project_pk")
        if not project_pk:
            return False

        try:
            project = Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            return False

        return project.contributors.filter(id=request.user.id).exists()

    def has_object_permission(self, request, view, obj):
        """
        Checks if the user is a contributor to the project associated with the object.

        This permission is used for detail views (retrieve, update, delete)
        of issues/comments.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # For an Issue, check if the user is a contributor to its project
        if isinstance(obj, Issue):
            return obj.project.contributors.filter(id=request.user.id).exists()

        # For a Comment, check if the user is a contributor to its issue's project
        if isinstance(obj, Comment):
            return obj.issue.project.contributors.filter(
                id=request.user.id
            ).exists()

        return False


class IsAuthor(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object (Issue or Comment)
    to modify or delete it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Checks if the user is the author of the object for write operations.

        Read (SAFE_METHODS) operations are allowed for contributors
        (handled by IsProjectContributor).
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user
