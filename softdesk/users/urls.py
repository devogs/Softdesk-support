from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import UserCreateAPIView

urlpatterns = [
    path("signup/", UserCreateAPIView.as_view(), name="signup"),
    path(
        "login/", TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "login/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
]
