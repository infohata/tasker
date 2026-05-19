from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Local app URLs wire in as the tasker_django.* apps land:
    # path("health/", include("tasker_django.health.urls")),
]
