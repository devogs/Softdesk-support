from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer


class UserCreateAPIView(generics.CreateAPIView):
    """
    API view for creating a new user (signup).

    Allows unauthenticated users to register.
    Performs age validation before user creation.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        """
        Performs the creation of a new user instance.

        Includes an additional check for age validity before saving the user.
        Hashes the user's password.

        Args:
            serializer (UserSerializer): The serializer instance containing
                                        validated user data.
        """
        age = self.request.data.get("age")

        if age is not None and int(age) < 15:
            return Response(
                {"age": "You must be at least 15 years old to register."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.save()
        user.set_password(self.request.data["password"])
        user.save()
