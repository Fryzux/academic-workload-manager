"""
Модуль тестов для веб-представлений Django (ПР5).
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "workload_manager.settings")
django.setup()

from django.test import Client, RequestFactory  # noqa: E402
from homepage.views import page_not_found  # noqa: E402
from models.teachers import Teacher  # noqa: E402
from models.disciplines import Discipline  # noqa: E402
from models.workloads import Workload, find_workload_by_id  # noqa: E402


def test_homepage_status_200():
    """Главная страница возвращает статус 200 и содержит заголовок."""
    client = Client()
    response = client.get("/")
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Система учета учебной нагрузки преподавателей" in content
    assert "Преподаватели" in content
    assert "Учебные поручения" in content


def test_teachers_list_status_200():
    """Список преподавателей возвращает 200 и содержит таблицу."""
    client = Client()
    response = client.get("/teachers/")
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Преподаватели кафедры" in content
    assert "Иванов Иван Иванович" in content


def test_teacher_detail_found():
    """Карточка существующего преподавателя возвращает статус 200."""
    client = Client()
    response = client.get("/teachers/1/")
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Иванов Иван Иванович" in content
    assert "Ставка по договору" in content


def test_teacher_detail_not_found():
    """Запрос несуществующего преподавателя возвращает статус 404."""
    client = Client()
    response = client.get("/teachers/999/")
    assert response.status_code == 404
    content = response.content.decode("utf-8")
    assert "404" in content


def test_workloads_list_status_200():
    """Список поручений возвращает статус 200 и содержит данные."""
    client = Client()
    response = client.get("/workloads/")
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Учебные поручения" in content
    assert "Итого" in content


def test_workload_detail_found():
    """Карточка существующего поручения возвращает статус 200."""
    client = Client()
    response = client.get("/workloads/1/")
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Поручение #1" in content
    assert "Объем часов по видам" in content


def test_workload_detail_not_found():
    """Запрос несуществующего поручения возвращает статус 404."""
    client = Client()
    response = client.get("/workloads/999/")
    assert response.status_code == 404
    content = response.content.decode("utf-8")
    assert "404" in content


def test_custom_page_not_found_view():
    """Прямой вызов обработчика 404 возвращает статус 404."""
    factory = RequestFactory()
    request = factory.get("/unknown-page/")
    response = page_not_found(request)
    assert response.status_code == 404
    content = response.content.decode("utf-8")
    assert "Ошибка 404" in content


def test_find_workload_by_id():
    """Проверка вспомогательной функции поиска поручения по ID."""
    t = Teacher(1, "Тест", "Доцент", "ИТ", 1.0)
    d = Discipline(1, "Тест", "ИТ", 1)
    w1 = Workload(10, t, d, 20.0, 30.0, 0.0, 10.0)
    w2 = Workload(20, t, d, 10.0, 10.0, 0.0, 0.0)
    items = [w1, w2]

    found = find_workload_by_id(items, 10)
    assert found is not None
    assert found.id == 10

    not_found = find_workload_by_id(items, 999)
    assert not_found is None
