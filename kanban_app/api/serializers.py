from rest_framework import serializers

from auth_app.models import User
from kanban_app.models import Board


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class BoardListSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(read_only=True)
    ticket_count = serializers.IntegerField(read_only=True)
    tasks_to_do_count = serializers.IntegerField(read_only=True)
    tasks_high_prio_count = serializers.IntegerField(read_only=True)
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    members = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=User.objects.all(), required=False
    )

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
            "members",
        ]

    def create(self, validated_data):
        members = validated_data.pop("members", [])
        board = Board.objects.create(**validated_data)
        board.members.set(members)
        return board
