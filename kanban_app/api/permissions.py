from rest_framework.permissions import BasePermission


class IsBoardMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.owner_id == request.user.id
            or obj.members.filter(id=request.user.id).exists()
        )
