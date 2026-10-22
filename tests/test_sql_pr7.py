"""
Модуль тестов для проверки реляционной базы данных SQLite и SQL-запросов (ПР7).
"""

import os
import sqlite3
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "workload_manager.settings")
django.setup()

from django.test import Client  # noqa: E402
from db.database import DB_PATH, get_connection, init_db  # noqa: E402
from db.import_json import (  # noqa: E402
    import_disciplines,
    import_teachers,
    import_workloads,
)


def test_sqlite_connection_and_foreign_keys():
    """Проверка подключения к SQLite и включения внешних ключей."""
    conn = get_connection()
    assert conn.row_factory == sqlite3.Row

    fk_status = conn.execute("PRAGMA foreign_keys").fetchone()[0]
    assert fk_status == 1
    conn.close()


def test_sqlite_tables_created():
    """Проверка наличия созданных таблиц в базе данных."""
    init_db()
    conn = get_connection()
    tables = [
        row["name"]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    ]
    assert "teachers" in tables
    assert "disciplines" in tables
    assert "workloads" in tables
    conn.close()


def test_sqlite_foreign_keys_constraints():
    """Проверка внешних ключей таблицы workloads."""
    conn = get_connection()
    fks = conn.execute("PRAGMA foreign_key_list(workloads)").fetchall()
    fk_tables = [row["table"] for row in fks]
    assert "teachers" in fk_tables
    assert "disciplines" in fk_tables
    conn.close()


def test_import_json_data():
    """Проверка импорта данных из JSON-файлов в SQLite."""
    conn = get_connection()
    import_teachers(conn)
    import_disciplines(conn)
    import_workloads(conn)
    conn.commit()

    teachers_count = conn.execute(
        "SELECT COUNT(*) AS cnt FROM teachers"
    ).fetchone()["cnt"]
    disciplines_count = conn.execute(
        "SELECT COUNT(*) AS cnt FROM disciplines"
    ).fetchone()["cnt"]
    workloads_count = conn.execute(
        "SELECT COUNT(*) AS cnt FROM workloads"
    ).fetchone()["cnt"]

    assert teachers_count >= 6
    assert disciplines_count >= 6
    assert workloads_count >= 4
    conn.close()


def test_sql_join_query():
    """Проверка выполнения запроса со связями (JOIN)."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT
            w.id,
            t.name AS teacher_name,
            d.name AS discipline_name,
            w.total_hours
        FROM workloads w
        JOIN teachers t ON w.teacher_id = t.id
        JOIN disciplines d ON w.discipline_id = d.id
        WHERE w.is_cancelled = 0
        ORDER BY w.id ASC;
        """
    ).fetchall()
    assert len(rows) > 0
    first = rows[0]
    assert first["teacher_name"] is not None
    assert first["discipline_name"] is not None
    assert first["total_hours"] > 0
    conn.close()


def test_sql_subquery_not_in():
    """Проверка подзапроса NOT IN для поиска свободных дисциплин."""
    conn = get_connection()
    free_disciplines = conn.execute(
        """
        SELECT id, name, semester
        FROM disciplines
        WHERE id NOT IN (
            SELECT discipline_id
            FROM workloads
            WHERE is_cancelled = 0
        );
        """
    ).fetchall()
    assert len(free_disciplines) > 0
    conn.close()


def test_sql_aggregates_and_group_by():
    """Проверка агрегатных функций и группировки (GROUP BY + HAVING)."""
    conn = get_connection()
    agg = conn.execute(
        """
        SELECT
            COUNT(DISTINCT w.id) AS cnt,
            SUM(w.total_hours) AS total,
            AVG(w.total_hours) AS avg_hours
        FROM workloads w
        WHERE w.is_cancelled = 0;
        """
    ).fetchone()
    assert agg["cnt"] > 0
    assert agg["total"] > 0
    assert agg["avg_hours"] > 0

    group_rows = conn.execute(
        """
        SELECT
            t.name,
            SUM(w.total_hours) AS total_assigned
        FROM teachers t
        JOIN workloads w ON t.id = w.teacher_id
        WHERE w.is_cancelled = 0
        GROUP BY t.id, t.name
        HAVING SUM(w.total_hours) >= 500.0;
        """
    ).fetchall()
    assert len(group_rows) > 0
    conn.close()


def test_available_disciplines_view():
    """Проверка веб-представления поиска свободных дисциплин."""
    client = Client()
    resp = client.get("/disciplines/available/")
    assert resp.status_code == 200
    content = resp.content.decode("utf-8")
    assert "Поиск свободных дисциплин" in content
    assert "Свободные дисциплины кафедры" in content

    resp_sem = client.get("/disciplines/available/?semester=4")
    assert resp_sem.status_code == 200


def test_statistics_view():
    """Проверка веб-представления статистики учебной нагрузки."""
    client = Client()
    resp = client.get("/workloads/statistics/")
    assert resp.status_code == 200
    content = resp.content.decode("utf-8")
    assert "Сводная статистика учебной нагрузки" in content
    assert "Активных поручений" in content
    assert "Преподавателей в работе" in content
    assert "Распределение нагрузки кафедры по семестрам" in content


def test_sqlite_file_location():
    """Проверка корректного расположения базы данных в каталоге data/."""
    assert DB_PATH.name == "workload.sqlite"
    assert DB_PATH.exists()
