"""
Маршруты URL для приложения disciplines.
"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.disciplines_list, name="disciplines_list"),
    path("add/", views.discipline_add, name="discipline_add"),
    path(
        "<int:discipline_id>/",
        views.discipline_detail,
        name="discipline_detail",
    ),
]
