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

    # This field will be used for input (POST/PUT/PATCH)
    # to set or update the assignee by username.
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
            "assignee_username",  # Include the write-only field for input
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
            return None # Allow assignee to be set to None/null

        try:
            assignee = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Assignee user does not exist.")

        # Ensure assignee is a contributor to the project
        # This context is typically available in viewsets for nested serializers
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
        # validated_data for assignee_username will already be the User object
        # if validate_assignee_username was called and returned the User object.
        # If it returned the username, then we need to fetch it here.
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
        # Pop assignee_username from validated_data. This value will be the User object
        # if validate_assignee_username was called and returned the User object.
        assignee_user_obj = validated_data.pop("assignee_username", None)

        # Handle assignee update based on whether assignee_username was provided
        if assignee_user_obj is not None:
            # If a User object was provided (from validation), set it
            instance.assignee = assignee_user_obj
        elif "assignee_username" in self.initial_data and self.initial_data["assignee_username"] == "":
            # If assignee_username was explicitly provided as an empty string, set assignee to None
            instance.assignee = None
        # If 'assignee_username' was not in initial_data, we do not change the existing instance.assignee

        # Update other fields using .get() to allow for partial updates (PATCH)
        # while also handling full PUT requests.
        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.tag = validated_data.get("tag", instance.tag)
        instance.priority = validated_data.get("priority", instance.priority)
        instance.status = validated_data.get("status", instance.status) # FIXED TYPO HERE

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
