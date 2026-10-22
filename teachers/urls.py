"""
Маршруты URL для приложения teachers.
"""

from django.urls import path
from . import views

app_name = "teachers"

urlpatterns = [
    path("", views.teachers, name="list"),
    path("", views.teachers, name="teachers"),
    path("add/", views.teacher_add, name="add"),
    path("add/", views.teacher_add, name="teacher_add"),
    path("<int:teacher_id>/", views.teacher_detail, name="detail"),
    path("<int:teacher_id>/", views.teacher_detail, name="teacher_detail"),
]
