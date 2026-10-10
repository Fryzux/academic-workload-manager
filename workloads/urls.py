"""
Маршруты URL для приложения workloads.
"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.workloads, name="workloads"),
    path("<int:workload_id>/", views.workload_detail, name="workload_detail"),
]
