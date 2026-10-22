"""
Маршруты URL для приложения disciplines.
"""

from django.urls import path
from . import views

app_name = "disciplines"

urlpatterns = [
    path("", views.disciplines_list, name="list"),
    path("", views.disciplines_list, name="disciplines_list"),
    path("available/", views.available_disciplines, name="available"),
    path("add/", views.discipline_add, name="add"),
    path("add/", views.discipline_add, name="discipline_add"),
    path(
        "<int:discipline_id>/",
        views.discipline_detail,
        name="detail",
    ),
    path(
        "<int:discipline_id>/",
        views.discipline_detail,
        name="discipline_detail",
    ),
]
