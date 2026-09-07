from rest_framework.exceptions import NotFound
from rest_framework.permissions import SAFE_METHODS, BasePermission

from kanban_app.models import Board

GUEST_EMAIL = "guest@kanmind.de"


class IsNotGuest(BasePermission):
    """Allows read access for everyone, blocks write actions for the guest demo account."""

    message = "The guest account is read-only."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.email != GUEST_EMAIL


class IsBoardMember(BasePermission):
    """Grants access to a board's owner or any of its members."""

    def has_object_permission(self, request, view, obj):
        return (
            obj.owner_id == request.user.id
            or obj.members.filter(id=request.user.id).exists()
        )


class IsBoardOwner(BasePermission):
    """Grants access only to a board's owner."""

    def has_object_permission(self, request, view, obj):
        return obj.owner_id == request.user.id


class IsBoardMemberToCreateTask(BasePermission):
    """Blocks task creation on a board the requesting user isn't a member of."""

    def has_permission(self, request, view):
        if "board" not in request.data:
            return True
        board = Board.objects.filter(pk=request.data.get("board")).first()
        if board is None:
            raise NotFound("Board not found.")
        return (
            board.owner_id == request.user.id
            or board.members.filter(id=request.user.id).exists()
        )


class IsTaskBoardMember(BasePermission):
    """Grants access to a task if the user is a member of the task's board."""

    def has_object_permission(self, request, view, obj):
        board = obj.board
        return (
            board.owner_id == request.user.id
            or board.members.filter(id=request.user.id).exists()
        )


class IsTaskCreatorOrBoardOwner(BasePermission):
    """Grants access to a task's creator or the owner of its board."""

    def has_object_permission(self, request, view, obj):
        return (
            obj.created_by_id == request.user.id
            or obj.board.owner_id == request.user.id
        )


class IsCommentAuthor(BasePermission):
    """Grants access only to the user who wrote the comment."""

    def has_object_permission(self, request, view, obj):
        return obj.author_id == request.user.id
