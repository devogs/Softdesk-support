from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the custom User model.

    Handles creation of new users and validation of fields.
    The password field is write-only to ensure it's not exposed in responses.
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "age",
            "can_be_contacted",
            "can_data_be_shared",
            "password",
            "created_time",
        ]
        read_only_fields = ["created_time"]

    def validate_age(self, value):
        """
        Validates the user's age.

        Raises a ValidationError if the age is less than 15 years,
        as per GDPR consent requirements.

        Args:
            value (int): The age provided by the user.

        Returns:
            int: The validated age.

        Raises:
            serializers.ValidationError: If the age is below 15.
        """
        if value is None:
            raise serializers.ValidationError("Age is required.")
        if value < 15:
            raise serializers.ValidationError(
                "You must be at least 15 years old to register."
            )
        return value

    def create(self, validated_data):
        """
        Creates and returns a new `User` instance, given the validated data.

        Hashes the password before saving the user.

        Args:
            validated_data (dict): Dictionary of validated data for the user.

        Returns:
            User: The newly created User instance.
        """
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
