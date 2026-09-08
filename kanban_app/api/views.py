from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import User
from kanban_app.api.permissions import (
    IsBoardMember,
    IsBoardMemberToCreateTask,
    IsBoardOwner,
    IsCommentAuthor,
    IsNotGuest,
    IsTaskBoardMember,
    IsTaskCreatorOrBoardOwner,
)
from kanban_app.api.serializers import (
    BoardDetailSerializer,
    BoardListSerializer,
    BoardUpdateSerializer,
    CommentSerializer,
    TaskSerializer,
    UserShortSerializer,
)
from kanban_app.models import Board, Comment, Task


class BoardViewSet(viewsets.ModelViewSet):
    """CRUD for boards, scoped to boards the requesting user owns or is a member of."""

    http_method_names = ["get", "post", "patch", "delete"]

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAuthenticated(), IsBoardOwner(), IsNotGuest()]
        return [IsAuthenticated(), IsBoardMember(), IsNotGuest()]

    def get_queryset(self):
        if self.action == "list":
            return self._annotated_queryset(self.request.user)
        return Board.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BoardDetailSerializer
        if self.action == "partial_update":
            return BoardUpdateSerializer
        return BoardListSerializer

    def _annotated_queryset(self, user):
        return (
            Board.objects.filter(Q(owner=user) | Q(members=user))
            .distinct()
            .annotate(
                member_count=Count("members", distinct=True),
                ticket_count=Count("tasks", distinct=True),
                tasks_to_do_count=Count(
                    "tasks", filter=Q(tasks__status="to-do"), distinct=True
                ),
                tasks_high_prio_count=Count(
                    "tasks", filter=Q(tasks__priority="high"), distinct=True
                ),
            )
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        board = self._annotated_queryset(request.user).get(pk=serializer.instance.pk)
        return Response(self.get_serializer(board).data, status=status.HTTP_201_CREATED)


class EmailCheckView(APIView):
    """Looks up a registered user by email, e.g. to validate board invites."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response(
                {"detail": "email is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        user = User.objects.filter(email=email).first()
        if user is None:
            return Response({"detail": "Email not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserShortSerializer(user).data, status=status.HTTP_200_OK)


class TaskViewSet(viewsets.ModelViewSet):
    """CRUD for tasks; the list action is limited to tasks on boards the user belongs to."""

    http_method_names = ["get", "post", "patch", "delete"]
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def get_queryset(self):
        if self.action != "list":
            return Task.objects.all()
        user = self.request.user
        return Task.objects.filter(
            Q(board__owner=user) | Q(board__members=user)
        ).distinct()

    def get_permissions(self):
        if self.action in ("retrieve", "partial_update"):
            return [IsAuthenticated(), IsTaskBoardMember(), IsNotGuest()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsTaskCreatorOrBoardOwner(), IsNotGuest()]
        return [IsAuthenticated(), IsBoardMemberToCreateTask(), IsNotGuest()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        if "board" in request.data:
            return Response(
                {"detail": "board cannot be changed."}, status=status.HTTP_400_BAD_REQUEST
            )
        return super().partial_update(request, *args, **kwargs)


class CommentListCreateView(generics.ListCreateAPIView):
    """Lists and creates comments on a task, restricted to the task's board members."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsNotGuest]

    def get_task(self):
        task = get_object_or_404(Task, pk=self.kwargs["task_id"])
        board = task.board
        is_member = (
            board.owner_id == self.request.user.id
            or board.members.filter(id=self.request.user.id).exists()
        )
        if not is_member:
            raise PermissionDenied("You must be a member of this board.")
        return task

    def get_queryset(self):
        return self.get_task().comments.select_related("author").all()

    def perform_create(self, serializer):
        serializer.save(task=self.get_task(), author=self.request.user)


class CommentDeleteView(generics.DestroyAPIView):
    """Deletes a comment; only the comment's own author is allowed to."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor, IsNotGuest]
    lookup_url_kwarg = "comment_id"

    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs["task_id"])


class AssignedToMeView(generics.ListAPIView):
    """Lists tasks where the requesting user is the assignee."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)


class ReviewingView(generics.ListAPIView):
    """Lists tasks where the requesting user is the reviewer."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)
