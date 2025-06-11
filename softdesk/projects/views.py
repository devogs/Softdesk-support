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


class ContributorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows project contributors to be viewed, added, or removed.

    This ViewSet is specifically for managing contributors associated with a project.
    """
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated] # Basic authentication, refine with specific permissions

    def get_queryset(self):
        """
        Returns the queryset of contributors for the current project.
        """
        project_pk = self.kwargs['project_pk']
        return Contributor.objects.filter(project_id=project_pk)

    def create(self, request, *args, **kwargs):
        """
        Adds a new contributor to the project.
        """
        project_pk = self.kwargs['project_pk']
        try:
            project = Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            return Response(
                {"detail": "Project not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Ensure the current user is the author of the project to add contributors
        if request.user != project.author:
            return Response(
                {"detail": "You do not have permission to add contributors to this project."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProjectContributorAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']

        try:
            user_to_add = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"detail": "User with this username does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if Contributor.objects.filter(project=project, user=user_to_add).exists():
            return Response(
                {"detail": "This user is already a contributor to this project."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Contributor.objects.create(project=project, user=user_to_add)
        return Response(
            {"detail": f"User '{username}' added as contributor."},
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        """
        Removes a contributor from the project.
        """
        project_pk = self.kwargs['project_pk']
        try:
            project = Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            return Response(
                {"detail": "Project not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Ensure the current user is the author of the project to remove contributors
        if request.user != project.author:
            return Response(
                {"detail": "You do not have permission to remove contributors from this project."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get the contributor instance to delete
        try:
            instance = self.get_object() # This will get the Contributor object based on URL lookup_field
        except Exception: # Handle case where get_object doesn't find it
            return Response(
                {"detail": "Contributor not found for this project."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Prevent removing the project author as a contributor
        if instance.user == project.author:
            return Response(
                {"detail": "The project author cannot be removed from contributors."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_destroy(instance)
        return Response(
            {"detail": "Contributor removed successfully."},
            status=status.HTTP_204_NO_CONTENT
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
        Adds explicit ordering to prevent UnorderedObjectListWarning.
        """
        return Project.objects.filter(contributors=self.request.user).distinct().order_by('-created_time')

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
