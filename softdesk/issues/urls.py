# issues/urls.py
from django.urls import path
from rest_framework import routers

from .views import CommentViewSet, IssueViewSet

# Using a SimpleRouter for base viewsets
issue_router = routers.SimpleRouter()
issue_router.register(r'', IssueViewSet, basename='issues') # No prefix here as it's within project_pk/issues/

comment_router = routers.SimpleRouter()
comment_router.register(r'', CommentViewSet, basename='comments') # No prefix here as it's within issue_pk/comments/

urlpatterns = [
    # URLs for Issues under a specific Project
    path(
        "projects/<int:project_pk>/issues/",
        IssueViewSet.as_view({"get": "list", "post": "create"}),
        name="project-issues-list",
    ),
    path(
        "projects/<int:project_pk>/issues/<int:pk>/",
        IssueViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
        name="project-issues-detail",
    ),
    # URLs for Comments under a specific Issue
    path(
        "projects/<int:project_pk>/issues/<int:issue_pk>/comments/",
        CommentViewSet.as_view({"get": "list", "post": "create"}),
        name="issue-comments-list",
    ),
    path(
        "projects/<int:project_pk>/issues/<int:issue_pk>/comments/<int:pk>/",
        CommentViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
        name="issue-comments-detail",
    ),
]
