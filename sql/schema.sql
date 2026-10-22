-- =========================================================
-- Academic Workload Manager: структура реляционной базы данных
-- =========================================================

PRAGMA foreign_keys = ON;

-- Таблица преподавателей
CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    position TEXT NOT NULL,
    department TEXT NOT NULL,
    rate REAL NOT NULL
);

-- Таблица дисциплин
CREATE TABLE IF NOT EXISTS disciplines (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    semester INTEGER NOT NULL
);

-- Таблица учебных поручений (нагрузки)
CREATE TABLE IF NOT EXISTS workloads (
    id INTEGER PRIMARY KEY,
    teacher_id INTEGER NOT NULL,
    discipline_id INTEGER NOT NULL,
    lectures REAL NOT NULL DEFAULT 0.0,
    practices REAL NOT NULL DEFAULT 0.0,
    labs REAL NOT NULL DEFAULT 0.0,
    exams REAL NOT NULL DEFAULT 0.0,
    total_hours REAL NOT NULL DEFAULT 0.0,
    is_cancelled INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    FOREIGN KEY (discipline_id) REFERENCES disciplines(id) ON DELETE CASCADE
);
