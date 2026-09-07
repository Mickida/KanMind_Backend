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
    def has_object_permission(self, request, view, obj):
        return (
            obj.owner_id == request.user.id
            or obj.members.filter(id=request.user.id).exists()
        )


class IsBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner_id == request.user.id


class IsBoardMemberToCreateTask(BasePermission):
    def has_permission(self, request, view):
        board = Board.objects.filter(pk=request.data.get("board")).first()
        if board is None:
            return True
        return (
            board.owner_id == request.user.id
            or board.members.filter(id=request.user.id).exists()
        )


class IsTaskBoardMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        board = obj.board
        return (
            board.owner_id == request.user.id
            or board.members.filter(id=request.user.id).exists()
        )


class IsTaskCreatorOrBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.created_by_id == request.user.id
            or obj.board.owner_id == request.user.id
        )


class IsCommentAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author_id == request.user.id
