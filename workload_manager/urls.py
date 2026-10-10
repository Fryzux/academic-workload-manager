"""
Конфигурация корневых маршрутов URL проекта workload_manager.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("teachers/", include("teachers.urls")),
    path("workloads/", include("workloads.urls")),
]

handler404 = "homepage.views.page_not_found"
