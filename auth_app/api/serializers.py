from rest_framework import serializers

from auth_app.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """Validates new-account data and creates the user with a hashed password."""

    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["fullname", "email", "password", "repeated_password"]

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop("repeated_password")
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Validates login credentials; authentication itself happens in the view."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        return value.lower()
