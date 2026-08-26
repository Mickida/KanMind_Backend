from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.api.serializers import RegistrationSerializer


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(self._auth_payload(user), status=status.HTTP_201_CREATED)

    def _auth_payload(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        return {
            "token": token.key,
            "fullname": user.fullname,
            "email": user.email,
            "user_id": user.id,
        }
