# softdesk/users/views.py
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer
# Import the new permission class we'll create
from .permissions import IsUserOwnerOrAdmin


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
        The password hashing is handled by the serializer's create method.

        Args:
            serializer (UserSerializer): The serializer instance containing
                                        validated user data.
        """
        age = self.request.data.get("age")

        if age is not None and int(age) < 15:
            return Response(
                {"age": "Vous devez avoir au moins 15 ans pour vous inscrire."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # The serializer's create method already handles set_password and save()
        serializer.save()


# softdesk/users/views.py
# ... (rest of your imports and UserCreateAPIView remain the same)

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed, updated, or deleted.

    This ViewSet provides 'retrieve', 'update', 'partial_update', and 'destroy'
    actions for user profiles. It enforces permissions to ensure users can
    only manage their own profiles, while administrative users have broader access.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsUserOwnerOrAdmin]

    def get_queryset(self):
        """
        Returns the base queryset of all User objects.

        The `IsUserOwnerOrAdmin` permission class will then handle object-level
        authorization, ensuring users can only interact with their own profile
        or that administrators have appropriate access.
        Ordering is added for consistent results.
        """
        # Return all users. Permissions will filter access.
        return User.objects.all().order_by('id')


    def destroy(self, request, *args, **kwargs):
        """
        Performs the deletion of a user account.

        This method handles the 'right to be forgotten' requirement by deleting
        the specified user instance.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A 204 No Content response upon successful deletion,
                      or an error response if the user cannot be deleted.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Compte utilisateur et données associées supprimés avec succès."},
            status=status.HTTP_204_NO_CONTENT
        )