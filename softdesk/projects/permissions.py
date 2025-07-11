from rest_framework import permissions


class IsAuthorOrContributor(permissions.BasePermission):
    """
    Custom permission to control access to projects.

    - Authenticated users can list or create projects.
    - Read permissions (GET, HEAD, OPTIONS) for a specific project are allowed
      to any user who is a contributor to that project.
    - Write permissions (PUT, PATCH, DELETE) for a specific project are
      only allowed to the author of that project.
    """

    def has_permission(self, request, view):
        """
        Checks if the user has general permission to access the project view.

        Allows authenticated users to list (GET) or create (POST) projects.

        Args:
            request (HttpRequest): The incoming request.
            view (APIView): The view being accessed.

        Returns:
            bool: True if permission is granted, False otherwise.
        """
        if request.user and request.user.is_authenticated:
            if request.method in permissions.SAFE_METHODS and view.basename == "projects":
                return True
            if request.method == "POST" and view.basename == "projects":
                return True
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """
        Checks if the user has object-level permission for a specific project.

        Allows specific actions on a project instance based on the user's role
        (author or contributor) and the requested method/action.

        Args:
            request (HttpRequest): The incoming request.
            view (APIView): The viewset handling the request.
            obj (Project): The project instance being accessed.

        Returns:
            bool: True if permission is granted, False otherwise.
        """

        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.contributors.all() or obj.author == request.user

        if request.method == "POST" and view.action == "contributors":
            return request.user == obj.author

        if request.method == "DELETE" and view.action == "contributors":
            return request.user == obj.author

        if request.method in ["PUT", "PATCH", "DELETE"]:
            return obj.author == request.user

        return False


class IsAuthor(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object to edit or delete it.

    This permission is intended for resources like Issues and Comments,
    where only the author can modify or delete their own entry.
    Read access is generally allowed if the user can access the parent resource.
    """

    def has_object_permission(self, request, view, obj):
        """
        Checks if the user has object-level permission for a specific resource.

        - Read permissions are allowed to any request (assumes parent resource
          permissions handle overall access).
        - Write permissions (PUT, PATCH, DELETE) are only allowed to the author.

        Args:
            request (HttpRequest): The incoming request.
            view (APIView): The view being accessed.
            obj (object): The resource object being accessed (e.g., Issue, Comment).

        Returns:
            bool: True if permission is granted, False otherwise.
        """
        # Read permissions are allowed to any request (SAFE_METHODS).
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions (PUT, PATCH, DELETE) are only allowed to the author.
        return obj.author == request.user
