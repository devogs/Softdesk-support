# issues/serializers.py
from rest_framework import serializers

from projects.models import Project
from users.models import User
from .models import Comment, Issue


class IssueSerializer(serializers.ModelSerializer):
    """
    Serializer for the Issue model.

    Handles the representation and validation of Issue instances.
    Includes fields for title, description, tags, priority, status,
    associated project, author, and assigned user.
    """

    author = serializers.ReadOnlyField(source="author.username")
    project = serializers.ReadOnlyField(source="project.title")
    assignee = serializers.ReadOnlyField(source="assignee.username")

    assignee_username = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "tag",
            "priority",
            "project",
            "status",
            "author",
            "assignee",
            "assignee_username",
            "created_time",
        ]
        read_only_fields = ["id", "project", "author", "created_time", "assignee"]

    def validate_project(self, value):
        """
        Validates that the project exists.
        """
        if not Project.objects.filter(pk=value.pk).exists():
            raise serializers.ValidationError("Project does not exist.")
        return value

    def validate_assignee_username(self, value):
        """
        Validates that the provided assignee_username exists and belongs
        to a contributor of the project.
        """
        if value is None:
            return None

        try:
            assignee = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Assignee user does not exist.")

        project_id = self.context["view"].kwargs["project_pk"]
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            raise serializers.ValidationError(
                "Project does not exist. Cannot validate assignee contributor status."
            )

        if not project.contributors.filter(id=assignee.id).exists():
            raise serializers.ValidationError(
                "Assigned user must be a contributor to this project."
            )
        return assignee

    def create(self, validated_data):
        """
        Creates and returns a new `Issue` instance.

        Sets the author and assignee based on validated data.
        """

        assignee_user_obj = validated_data.pop("assignee_username", None)

        issue = Issue.objects.create(**validated_data)
        if assignee_user_obj:
            issue.assignee = assignee_user_obj
            issue.save()
        return issue

    def update(self, instance, validated_data):
        """
        Updates and returns an existing `Issue` instance.

        Handles updating the assignee if `assignee_username` is provided.
        """

        assignee_user_obj = validated_data.pop("assignee_username", None)

        if assignee_user_obj is not None:
            instance.assignee = assignee_user_obj
        elif "assignee_username" in self.initial_data and self.initial_data["assignee_username"] == "":
            instance.assignee = None

        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.tag = validated_data.get("tag", instance.tag)
        instance.priority = validated_data.get("priority", instance.priority)
        instance.status = validated_data.get("status", instance.status)

        instance.save()
        return instance


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Comment model.

    Includes the author's username and the ID of the associated issue.
    """

    author = serializers.ReadOnlyField(source="author.username")
    issue = serializers.ReadOnlyField(source="issue.id")

    class Meta:
        model = Comment
        fields = ["id", "uuid", "description", "issue", "author", "created_time"]
        read_only_fields = ["id", "uuid", "issue", "author", "created_time"]
