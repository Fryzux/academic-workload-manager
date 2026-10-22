"""
Модуль импорта существующих данных из JSON-файлов в таблицы SQLite.
"""

import json
from pathlib import Path

from db.database import BASE_DIR, get_connection, init_db

TEACHERS_FILE = BASE_DIR / "data" / "teachers.json"
DISCIPLINES_FILE = BASE_DIR / "data" / "disciplines.json"
WORKLOADS_FILE = BASE_DIR / "data" / "workloads.json"


def load_json(filepath: Path):
    """Загрузить JSON-данные из файла."""
    with open(filepath, encoding="utf-8") as file:
        return json.load(file)


def import_teachers(conn):
    """Импортировать преподавателей в таблицу teachers."""
    teachers = load_json(TEACHERS_FILE)
    conn.executemany(
        """
        INSERT OR REPLACE INTO teachers (
            id, name, position, department, rate
        ) VALUES (?, ?, ?, ?, ?)
        """,
        [
            (
                t["id"],
                t["name"],
                t["position"],
                t["department"],
                float(t["rate"]),
            )
            for t in teachers
        ],
    )


def import_disciplines(conn):
    """Импортировать дисциплины в таблицу disciplines."""
    disciplines = load_json(DISCIPLINES_FILE)
    conn.executemany(
        """
        INSERT OR REPLACE INTO disciplines (
            id, name, department, semester
        ) VALUES (?, ?, ?, ?)
        """,
        [
            (
                d["id"],
                d["name"],
                d["department"],
                int(d["semester"]),
            )
            for d in disciplines
        ],
    )


def import_workloads(conn):
    """Импортировать учебные поручения в таблицу workloads."""
    workloads = load_json(WORKLOADS_FILE)
    conn.executemany(
        """
        INSERT OR REPLACE INTO workloads (
            id,
            teacher_id,
            discipline_id,
            lectures,
            practices,
            labs,
            exams,
            total_hours,
            is_cancelled
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                w["id"],
                int(w["teacher_id"]),
                int(w["discipline_id"]),
                float(w.get("lectures", 0.0)),
                float(w.get("practices", 0.0)),
                float(w.get("labs", 0.0)),
                float(w.get("exams", 0.0)),
                float(w.get("total_hours", 0.0)),
                1 if w.get("is_cancelled") else 0,
            )
            for w in workloads
        ],
    )


def main():
    """Выполнить полный цикл инициализации и импорта данных."""
    init_db()
    conn = get_connection()
    try:
        import_teachers(conn)
        import_disciplines(conn)
        import_workloads(conn)
        conn.commit()
        print("Данные успешно импортированы в базу данных SQLite.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
