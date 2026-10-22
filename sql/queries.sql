-- =========================================================
-- Academic Workload Manager: SQL-запросы предметной области
-- =========================================================

-- Запрос 1. Выборка списка всех преподавателей с сортировкой по ФИО
SELECT
    id,
    name,
    position,
    department,
    rate
FROM teachers
ORDER BY name ASC;

-- Запрос 2. Выборка списка всех дисциплин по семестрам
SELECT
    id,
    name,
    department,
    semester
FROM disciplines
ORDER BY semester ASC, name ASC;

-- Запрос 3. Фильтрация преподавателей с полной ставкой (WHERE)
SELECT
    id,
    name,
    position,
    department,
    rate
FROM teachers
WHERE rate >= 1.0
ORDER BY name ASC;

-- Запрос 4. Фильтрация учебных поручений с высокой нагрузкой (WHERE)
SELECT
    id,
    teacher_id,
    discipline_id,
    total_hours,
    is_cancelled
FROM workloads
WHERE total_hours > 400.0 AND is_cancelled = 0
ORDER BY total_hours DESC;

-- Запрос 5. Активные поручения со сведениями о преподавателях и дисциплинах (JOIN)
SELECT
    w.id,
    w.teacher_id,
    w.discipline_id,
    t.name AS teacher_name,
    t.position AS teacher_position,
    d.name AS discipline_name,
    d.semester,
    w.lectures,
    w.practices,
    w.labs,
    w.exams,
    w.total_hours
FROM workloads w
JOIN teachers t ON w.teacher_id = t.id
JOIN disciplines d ON w.discipline_id = d.id
WHERE w.is_cancelled = 0
ORDER BY t.name ASC, d.name ASC;

-- Запрос 6. Детальные поручения конкретного преподавателя (параметризованный JOIN)
SELECT
    w.id,
    d.name AS discipline_name,
    d.semester,
    w.lectures,
    w.practices,
    w.labs,
    w.exams,
    w.total_hours,
    w.is_cancelled
FROM workloads w
JOIN disciplines d ON w.discipline_id = d.id
WHERE w.teacher_id = ?
ORDER BY d.semester ASC;

-- Запрос 7. Свободные дисциплины, на которые не назначены поручения (подзапрос NOT IN)
SELECT
    d.id,
    d.name,
    d.department,
    d.semester
FROM disciplines d
WHERE d.id NOT IN (
    SELECT w.discipline_id
    FROM workloads w
    WHERE w.is_cancelled = 0
)
ORDER BY d.semester ASC, d.name ASC;

-- Запрос 8. Общая статистика кафедры (агрегатные функции COUNT, SUM, AVG)
SELECT
    COUNT(DISTINCT w.id) AS total_active_workloads,
    COUNT(DISTINCT w.teacher_id) AS active_teachers_count,
    COALESCE(SUM(w.total_hours), 0.0) AS total_hours_sum,
    COALESCE(AVG(w.total_hours), 0.0) AS avg_hours_per_workload
FROM workloads w
WHERE w.is_cancelled = 0;

-- Запрос 9. Распределение учебной нагрузки по преподавателям (LEFT JOIN + GROUP BY)
SELECT
    t.id AS teacher_id,
    t.name AS teacher_name,
    t.position,
    t.rate,
    (t.rate * 900.0) AS planned_hours,
    COUNT(w.id) AS assignments_count,
    COALESCE(SUM(w.total_hours), 0.0) AS assigned_hours
FROM teachers t
LEFT JOIN workloads w ON t.id = w.teacher_id AND w.is_cancelled = 0
GROUP BY t.id, t.name, t.position, t.rate
ORDER BY assigned_hours DESC;

-- Запрос 10. Преподаватели с повышенной нагрузкой более 500 часов (GROUP BY + HAVING)
SELECT
    t.name AS teacher_name,
    t.position,
    t.rate,
    SUM(w.total_hours) AS total_assigned_hours
FROM teachers t
JOIN workloads w ON t.id = w.teacher_id
WHERE w.is_cancelled = 0
GROUP BY t.id, t.name, t.position, t.rate
HAVING SUM(w.total_hours) >= 500.0
ORDER BY total_assigned_hours DESC;

-- Запрос 11. Суммарная нагрузка кафедры в разрезе семестров (JOIN + GROUP BY + SUM)
SELECT
    d.semester,
    COUNT(w.id) AS assignments_count,
    SUM(w.total_hours) AS semester_hours
FROM workloads w
JOIN disciplines d ON w.discipline_id = d.id
WHERE w.is_cancelled = 0
GROUP BY d.semester
ORDER BY d.semester ASC;

-- Запрос 12. Поиск преподавателей со свободным резервом ставки (GROUP BY + HAVING)
SELECT
    t.id,
    t.name,
    t.rate,
    (t.rate * 900.0) AS max_planned_hours,
    COALESCE(SUM(w.total_hours), 0.0) AS current_hours,
    ((t.rate * 900.0) - COALESCE(SUM(w.total_hours), 0.0)) AS free_hours
FROM teachers t
LEFT JOIN workloads w ON t.id = w.teacher_id AND w.is_cancelled = 0
GROUP BY t.id, t.name, t.rate
HAVING free_hours > 0.0
ORDER BY free_hours DESC;
