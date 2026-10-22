"""
Маршруты URL для приложения teachers.
"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.teachers, name="teachers"),
    path("add/", views.teacher_add, name="teacher_add"),
    path("<int:teacher_id>/", views.teacher_detail, name="teacher_detail"),
]
