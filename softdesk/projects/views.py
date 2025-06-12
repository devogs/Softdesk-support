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
                {"detail": "Projet introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.user != project.author:
            return Response(
                {"detail": "Vous n'avez pas la permission d'ajouter des contributeurs à ce projet."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProjectContributorAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']

        try:
            user_to_add = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"detail": "Ce nom d'utilisateur n'existe pas."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if Contributor.objects.filter(project=project, user=user_to_add).exists():
            return Response(
                {"detail": "Cet utilisateur est déjà un contributeur de ce projet."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Contributor.objects.create(project=project, user=user_to_add)
        return Response(
            {"detail": f"L'utilisateur '{username}' a été ajouté comme contributeur."},
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
                {"detail": "Projet introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.user != project.author:
            return Response(
                {"detail": "Vous n'avez pas la permission de retirer des contributeurs de ce projet."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            instance = self.get_object()
        except Exception:
            return Response(
                {"detail": "L'utilisateur n'est pas un contributeur de ce projet."},
                status=status.HTTP_404_NOT_FOUND
            )

        if instance.user == project.author:
            return Response(
                {"detail": "L'auteur du projet ne peut pas être retiré des contributeurs."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_destroy(instance)
        return Response(
            {"detail": "Contributeur retiré avec succès."},
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
        Returns a queryset of projects based on user's role and action.
        - Superusers/staff can see all projects.
        - For 'retrieve' action (detail view), all projects are returned for permission checking (to get 403 instead of 404).
        - For other actions (list, create, update, delete) and non-admin users,
          only projects where the user is author or contributor are returned.
        """
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return Project.objects.all().order_by('id')

        if self.action == 'retrieve':
            return Project.objects.all().order_by('id')

        authored_projects = Project.objects.filter(author=user)
        contributed_projects = Project.objects.filter(contributors=user)
        return (authored_projects | contributed_projects).distinct().order_by('id')

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
                    {"detail": "Vous n'avez pas la permission d'ajouter des contributeurs."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = ProjectContributorAddSerializer(data=request.data)
            if serializer.is_valid():
                username = serializer.validated_data["username"]
                try:
                    user_to_add = User.objects.get(username=username)
                except User.DoesNotExist:
                    return Response(
                        {"detail": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND
                    )

                if Contributor.objects.filter(
                    project=project, user=user_to_add
                ).exists():
                    return Response(
                        {"detail": "L'utilisateur est déjà un contributeur de ce projet."},
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
                    {"detail": "Vous n'avez pas la permission de retirer des contributeurs"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            username = request.data.get("username")
            if not username:
                return Response(
                    {"detail": "Le nom d'utilisateur est requis pour retirer un contributeur."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                user_to_remove = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response(
                    {"detail": "L'utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND
                )

            if user_to_remove == project.author:
                return Response(
                    {"detail": "L'auteur du projet ne peut pas être retiré des contributeurs."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                contributor_to_delete = Contributor.objects.get(
                    project=project, user=user_to_remove
                )
                contributor_to_delete.delete()
                return Response(
                    {"detail": "Contributeur retiré avec succès."},
                    status=status.HTTP_204_NO_CONTENT,
                )
            except Contributor.DoesNotExist:
                return Response(
                    {"detail": "L'utilisateur n'est pas un contributeur de ce projet."},
                    status=status.HTTP_404_NOT_FOUND,
                )
