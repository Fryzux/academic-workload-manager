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


def test_teachers_search_and_filter():
    """Поиск преподавателя по ФИО и фильтрация по соответствию норме."""
    client = Client()
    resp_q = client.get("/teachers/?q=Иванов")
    assert resp_q.status_code == 200
    assert "Иванов" in resp_q.content.decode("utf-8")

    resp_comp = client.get("/teachers/?compliance=norm")
    assert resp_comp.status_code == 200


def test_workloads_filter_and_search():
    """Фильтрация поручений по статусу и строке поиска."""
    client = Client()
    resp_active = client.get("/workloads/?status=active")
    assert resp_active.status_code == 200

    resp_canc = client.get("/workloads/?status=cancelled")
    assert resp_canc.status_code == 200

    resp_search = client.get("/workloads/?q=Иванов")
    assert resp_search.status_code == 200


def test_workload_toggle_action_and_404():
    """Переключение активности поручения и проверка 404 на несуществующем."""
    client = Client()
    # 404 на несуществующем ID
    resp_404 = client.get("/workloads/999/toggle/")
    assert resp_404.status_code == 404

    # Успешный редирект при переключении существующего
    resp_toggle = client.get("/workloads/1/toggle/")
    assert resp_toggle.status_code == 302
    assert "/workloads/1/" in resp_toggle.headers["Location"]

    # Возврат статуса обратно
    resp_restore = client.get("/workloads/1/toggle/")
    assert resp_restore.status_code == 302
