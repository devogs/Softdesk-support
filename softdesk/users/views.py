# users/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import User
from .serializers import UserSerializer

class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # Retrieve age from the request for GDPR validation
        age = self.request.data.get('age')

        # Validate age according to GDPR (must be over 15)
        # This validation is also in the serializer, but a double check here is possible
        # The legal age to give consent alone is 15 years [cite: 27]
        if age is not None and int(age) < 15:
            return Response(
                {"age": "You must be at least 15 years old to register."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save the user with the hashed password
        user = serializer.save()
        user.set_password(self.request.data['password'])
        user.save()
