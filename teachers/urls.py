"""
Маршруты URL для приложения teachers.
"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.teachers, name="teachers"),
    path("<int:teacher_id>/", views.teacher_detail, name="teacher_detail"),
]
