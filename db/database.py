"""
Модуль подключения и инициализации базы данных SQLite.
"""

from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "workload.sqlite"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def get_connection():
    """Создать и вернуть настроенное подключение к SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Создать таблицы базы данных на основе файла sql/schema.sql."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    try:
        with open(SCHEMA_PATH, encoding="utf-8") as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print(f"База данных успешно инициализирована: {DB_PATH}")
