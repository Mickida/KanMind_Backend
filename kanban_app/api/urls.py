from django.urls import path
from rest_framework.routers import DefaultRouter

from kanban_app.api.views import (
    AssignedToMeView,
    BoardViewSet,
    CommentListCreateView,
    EmailCheckView,
    ReviewingView,
    TaskViewSet,
)

router = DefaultRouter()
router.register("boards", BoardViewSet, basename="board")
router.register("tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("email-check/", EmailCheckView.as_view(), name="email-check"),
    path("tasks/assigned-to-me/", AssignedToMeView.as_view(), name="tasks-assigned-to-me"),
    path("tasks/reviewing/", ReviewingView.as_view(), name="tasks-reviewing"),
    path(
        "tasks/<int:task_id>/comments/",
        CommentListCreateView.as_view(),
        name="task-comments",
    ),
] + router.urls
