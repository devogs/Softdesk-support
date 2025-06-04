from django.conf import settings
from django.db import models


class Project(models.Model):
    """
    Represents a project in the SoftDesk application.

    Each project has a title, description, type, an author,
    and a list of contributors.
    """

    TYPE_CHOICES = [
        ("back-end", "Back-End"),
        ("front-end", "Front-End"),
        ("ios", "iOS"),
        ("android", "Android"),
    ]

    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_projects",
    )
    contributors = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="Contributor", related_name="contributed_projects"
    )
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns the project's title as its string representation.
        """
        return self.title


class Contributor(models.Model):
    """
    Intermediate model representing a user's contribution to a project.

    Defines the many-to-many relationship between User and Project.
    Ensures a user can only be a contributor to a project once.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "project")

    def __str__(self):
        """
        Returns a string representation of the contributor relationship.
        """
        return f"{self.user.username} contributes to {self.project.title}"
