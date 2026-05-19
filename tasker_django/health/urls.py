from django.urls import path

from tasker_django.health.views import health_view

app_name = "health"

urlpatterns = [
    path("", health_view, name="check"),
]
