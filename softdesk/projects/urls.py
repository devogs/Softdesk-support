# softdesk/projects/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from . import views as project_views
from issues import views as issue_views


router = DefaultRouter()
router.register(r"projects", project_views.ProjectViewSet, basename="projects")

projects_router = NestedDefaultRouter(router, r"projects", lookup="project")
projects_router.register(
    r"users", project_views.ContributorViewSet, basename="project-contributors"
)
projects_router.register(r"issues", issue_views.IssueViewSet, basename="project-issues")

issues_router = NestedDefaultRouter(projects_router, r"issues", lookup="issue")
issues_router.register(
    r"comments", issue_views.CommentViewSet, basename="issue-comments"
)

urlpatterns = [
    path("", include(router.urls)),           # Includes /projects/
    path("", include(projects_router.urls)),  # Includes /projects/{project_pk}/users/, /projects/{project_pk}/issues/
    path("", include(issues_router.urls)),    # Includes /projects/{project_pk}/issues/{issue_pk}/comments/
]
