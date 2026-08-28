from django.urls import path
from rest_framework.routers import DefaultRouter

from kanban_app.api.views import BoardViewSet, EmailCheckView

router = DefaultRouter()
router.register("boards", BoardViewSet, basename="board")

urlpatterns = [
    path("email-check/", EmailCheckView.as_view(), name="email-check"),
] + router.urls
