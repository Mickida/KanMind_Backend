from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import User
from kanban_app.api.permissions import IsBoardMember, IsBoardOwner
from kanban_app.api.serializers import (
    BoardDetailSerializer,
    BoardListSerializer,
    BoardUpdateSerializer,
    UserShortSerializer,
)
from kanban_app.models import Board


class BoardViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated(), IsBoardMember()]

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
