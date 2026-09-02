from rest_framework.permissions import BasePermission


class IsBoardMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.owner_id == request.user.id
            or obj.members.filter(id=request.user.id).exists()
        )


class IsBoardOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner_id == request.user.id


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
