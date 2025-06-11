# issues/models.py
from django.conf import settings
from django.db import models
import uuid

from projects.models import Project


class Issue(models.Model):
    """
    Represents an issue within a specific project.

    Issues have a title, description, tags, priority, status,
    an author, and an assigned user.
    """

    TAG_CHOICES = [
        ("bug", "Bug"),
        ("feature", "Feature"),
        ("task", "Task"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    STATUS_CHOICES = [
        ("to do", "To Do"),
        ("in progress", "In Progress"),
        ("finished", "Finished"),
    ]

    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048)
    tag = models.CharField(max_length=20, choices=TAG_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="issues"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="to do"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_issues",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_issues",
    )
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns the issue's title as its string representation.
        """
        return self.title


class Comment(models.Model):
    """
    Represents a comment on a specific issue.

    Each comment has a description, is linked to an issue, and has an author.
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    description = models.TextField(max_length=2048)
    issue = models.ForeignKey(
        Issue, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_comments",
    )
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a truncated description of the comment as its string representation.
        """
        return f"Comment on '{self.issue.title}': {self.description[:50]}..."
