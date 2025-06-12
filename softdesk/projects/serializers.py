from rest_framework import serializers

from users.models import User  # Used in ProjectContributorAddSerializer
from .models import Contributor, Project


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the Project model.

    Includes the author's username and a count of contributors.
    Author is read-only and set by the view.
    """

    author = serializers.ReadOnlyField(source="author.username")
    contributors_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "type",
            "author",
            "contributors_count",
            "created_time",
        ]
        read_only_fields = ["created_time", "author"]

    def get_contributors_count(self, obj) -> int:
        """
        Returns the number of contributors for a given project.
        """
        return obj.contributors.count()

    def create(self, validated_data):
        """
        Creates and returns a new `Project` instance.

        The author field is expected to be set by the view.

        Args:
            validated_data (dict): Dictionary of validated data for the project.

        Returns:
            Project: The newly created Project instance.
        """
        return Project.objects.create(**validated_data)


class ContributorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Contributor model.

    Displays the username of the contributing user and the title of the project.
    """

    user = serializers.ReadOnlyField(source="user.username")
    project = serializers.ReadOnlyField(source="project.title")

    class Meta:
        model = Contributor
        fields = ["id", "user", "project"]
        read_only_fields = ["id"]


class ProjectContributorAddSerializer(serializers.Serializer):
    """
    Serializer for adding a user as a contributor to a project.

    Requires only the username of the user to be added.
    """

    username = serializers.CharField(max_length=150)

    def validate_username(self, value):
        """
        Validates that the provided username corresponds to an existing user.

        Args:
            value (str): The username to validate.

        Returns:
            str: The validated username.

        Raises:
            serializers.ValidationError: If no user with the given username exists.
        """
        try:
            User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this username does not exist.")
        return value
