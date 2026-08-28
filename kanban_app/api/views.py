from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import User
from kanban_app.api.serializers import UserShortSerializer


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
