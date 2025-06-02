# users/serializers.py
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True) # Password will not be returned in responses

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'age', 'can_be_contacted', 'can_data_be_shared', 'password', 'created_time']
        read_only_fields = ['created_time'] # Timestamp is automatically generated [cite: 80]

    def validate_age(self, value):
        # The legal age to give consent alone is 15 years [cite: 27]
        if value < 15:
            raise serializers.ValidationError("You must be at least 15 years old to register.")
        return value

    def create(self, validated_data):
        # Retrieve the password and remove it from validated data for secure processing
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password) # Hash the password
        user.save()
        return user