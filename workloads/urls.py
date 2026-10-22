"""
Маршруты URL для приложения workloads.
"""

from django.urls import path
from . import views

app_name = "workloads"

urlpatterns = [
    path("", views.workloads, name="list"),
    path("", views.workloads, name="workloads"),
    path("<int:workload_id>/", views.workload_detail, name="detail"),
    path("<int:workload_id>/", views.workload_detail, name="workload_detail"),
    path(
        "<int:workload_id>/toggle/",
        views.workload_toggle,
        name="toggle",
    ),
    path(
        "<int:workload_id>/toggle/",
        views.workload_toggle,
        name="workload_toggle",
    ),
]
