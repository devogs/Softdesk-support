from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import User
from .models import Contributor, Project
from .permissions import IsAuthorOrContributor
from .serializers import (
    ContributorSerializer,
    ProjectContributorAddSerializer,
    ProjectSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed, created, updated, or deleted.

    Includes custom actions for managing project contributors.
    Permissions ensure only authorized users can access and modify projects.
    """

    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrContributor]

    def get_queryset(self):
        """
        Returns the queryset of projects for the current request.

        Users can only see projects they are contributing to or are the author of.
        """
        return Project.objects.filter(contributors=self.request.user).distinct()

    def perform_create(self, serializer):
        """
        Sets the author of the project to the current authenticated user
        and automatically adds the author as a contributor.
        """
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(user=self.request.user, project=project)

    @action(detail=True, methods=["get", "post", "delete"], url_path="users")
    def contributors(self, request, pk=None):
        """
        Manages contributors for a specific project.

        GET: Lists all contributors for the project.
        POST: Adds a user as a contributor to the project.
              Only the project author can perform this action.
        DELETE: Removes a contributor from the project.
                Only the project author can perform this action,
                and the author cannot remove themselves.
        """
        project = self.get_object()  # Ensures object-level permissions are checked

        if request.method == "GET":
            contributors = Contributor.objects.filter(project=project)
            serializer = ContributorSerializer(contributors, many=True)
            return Response(serializer.data)

        elif request.method == "POST":
            if project.author != request.user:
                return Response(
                    {"detail": "You do not have permission to add contributors."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = ProjectContributorAddSerializer(data=request.data)
            if serializer.is_valid():
                username = serializer.validated_data["username"]
                try:
                    user_to_add = User.objects.get(username=username)
                except User.DoesNotExist:
                    return Response(
                        {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
                    )

                if Contributor.objects.filter(
                    project=project, user=user_to_add
                ).exists():
                    return Response(
                        {"detail": "User is already a contributor to this project."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                Contributor.objects.create(project=project, user=user_to_add)
                return Response(
                    ContributorSerializer(
                        Contributor.objects.get(project=project, user=user_to_add)
                    ).data,
                    status=status.HTTP_201_CREATED,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == "DELETE":
            if project.author != request.user:
                return Response(
                    {"detail": "You do not have permission to remove contributors."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            username = request.data.get("username")
            if not username:
                return Response(
                    {"detail": "Username is required to remove a contributor."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                user_to_remove = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response(
                    {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
                )

            if user_to_remove == project.author:
                return Response(
                    {"detail": "The project author cannot be removed from contributors."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                contributor_to_delete = Contributor.objects.get(
                    project=project, user=user_to_remove
                )
                contributor_to_delete.delete()
                return Response(
                    {"detail": "Contributor removed successfully."},
                    status=status.HTTP_204_NO_CONTENT,
                )
            except Contributor.DoesNotExist:
                return Response(
                    {"detail": "User is not a contributor to this project."},
                    status=status.HTTP_404_NOT_FOUND,
                )
