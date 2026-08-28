from django.urls import path

from kanban_app.api.views import EmailCheckView

urlpatterns = [
    path("email-check/", EmailCheckView.as_view(), name="email-check"),
]
