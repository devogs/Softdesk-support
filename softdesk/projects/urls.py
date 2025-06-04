from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProjectViewSet


router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="projects")

urlpatterns = [
    path("", include(router.urls)),
]
