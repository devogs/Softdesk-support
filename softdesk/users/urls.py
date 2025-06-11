# softdesk/users/urls.py
"""
URL patterns for the users application, including authentication and user profile management.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import UserCreateAPIView, UserViewSet

# Initialize DefaultRouter for UserViewSet to manage user profiles.
# This router automatically generates standard RESTful URLs for list, retrieve,
# update, and delete operations (e.g., /users/ and /users/{id}/).
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Existing authentication and registration endpoints:
    # POST /api/signup/        - Endpoint for new user registration.
    path("signup/", UserCreateAPIView.as_view(), name="signup"),
    # POST /api/login/         - Endpoint to obtain JWT access and refresh tokens.
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # POST /api/login/refresh/ - Endpoint to refresh an expired JWT access token.
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # New user profile management endpoints:
    # These URLs are handled by the UserViewSet via the router.
    # When included in the main project URLs under '/api/', they will form:
    # GET /api/users/           - List all users (admin only, controlled by permissions).
    # GET /api/users/{id}/      - Retrieve a specific user's profile (owner or admin).
    # PUT /api/users/{id}/      - Update a specific user's profile (owner or admin).
    # PATCH /api/users/{id}/    - Partially update a specific user's profile (owner or admin).
    # DELETE /api/users/{id}/   - Delete a specific user's profile (owner or admin).
    path('', include(router.urls)),
]
