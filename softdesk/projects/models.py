# projects/models.py
from django.db import models
from django.conf import settings

class Project(models.Model):
    TYPE_CHOICES = [
        ('back-end', 'Back-End'),
        ('front-end', 'Front-End'),
        ('ios', 'iOS'),
        ('android', 'Android'),
    ]

    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='authored_projects'
    )
    contributors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Contributor',
        related_name='contributed_projects'
    )
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Contributor(models.Model):

    PERMISSION_CHOICES = [
        ('read', 'Read'),
        ('write', 'Write'),
        ('manage', 'Manage'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'project')

    def __str__(self):
        return f"{self.user.username} contributes to {self.project.title}"
