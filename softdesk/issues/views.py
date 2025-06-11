# issues/views.py
from rest_framework import status, viewsets
from rest_framework.response import Response

from projects.models import Project
from .models import Comment, Issue
from .permissions import IsAuthor, IsProjectContributor
from .serializers import CommentSerializer, IssueSerializer


class IssueViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows issues to be viewed, created, updated, or deleted.

    Issues are nested under projects: /projects/{project_pk}/issues/
    Permissions ensure only project contributors can access issues,
    and only the author can modify/delete their issues.
    """

    serializer_class = IssueSerializer
    permission_classes = [IsProjectContributor, IsAuthor]

    def get_queryset(self):
        """
        Returns the queryset of issues for the current request,
        ordered to ensure consistent pagination.
        """
        project_pk = self.kwargs.get('project_pk')
        if project_pk:
            return Issue.objects.filter(project=project_pk).order_by('-created_time')

        return Issue.objects.all().order_by('-created_time')

    def perform_create(self, serializer):
        """
        Sets the project and author for a new issue.

        The project is taken from the URL, and the author is the current user.
        The assignee is set during serializer.save() in IssueSerializer.
        """
        project_pk = self.kwargs["project_pk"]
        try:
            project = Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            return Response(
                {"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if the current user is a contributor to this project (handled by permission, but double check)
        if not project.contributors.filter(id=self.request.user.id).exists():
            return Response(
                {"detail": "You are not a contributor to this project."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer.save(project=project, author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows comments to be viewed, created, updated, or deleted.

    Comments are nested under issues: /projects/{project_pk}/issues/{issue_pk}/comments/
    Permissions ensure only project contributors can access comments,
    and only the author can modify/delete their comments.
    """

    serializer_class = CommentSerializer
    permission_classes = [IsProjectContributor, IsAuthor]

    def get_queryset(self):
        """
        Returns comments for the specific issue identified by issue_pk in the URL.
        """
        issue_pk = self.kwargs["issue_pk"]
        return Comment.objects.filter(issue_id=issue_pk)

    def perform_create(self, serializer):
        """
        Sets the issue and author for a new comment.

        The issue is taken from the URL, and the author is the current user.
        """
        issue_pk = self.kwargs["issue_pk"]
        try:
            issue = Issue.objects.get(pk=issue_pk)
        except Issue.DoesNotExist:
            return Response(
                {"detail": "Issue not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if the current user is a contributor to this issue's project
        # (handled by permission, but double check)
        if not issue.project.contributors.filter(id=self.request.user.id).exists():
            return Response(
                {"detail": "You are not a contributor to this project."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer.save(issue=issue, author=self.request.user)
