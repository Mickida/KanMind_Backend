from rest_framework import serializers

from auth_app.models import User


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]
