"""
Представления для приложения workloads.
"""

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from db.database import get_connection
from models.workloads import find_workload_by_id
from storage import (
    load_disciplines,
    load_teachers,
    load_workloads,
    save_workloads,
)


def _load_data():
    """Загрузить данные преподавателей, дисциплин и поручений."""
    base = settings.BASE_DIR
    t_path = str(base / "data" / "teachers.json")
    d_path = str(base / "data" / "disciplines.json")
    w_path = str(base / "data" / "workloads.json")

    teachers = load_teachers(t_path)
    disciplines = load_disciplines(d_path)
    workloads = load_workloads(w_path, teachers, disciplines)
    return teachers, disciplines, workloads, w_path


def workloads(request: HttpRequest) -> HttpResponse:
    """Отобразить общий список поручений с фильтрацией и поиском."""
    _, _, all_items, _ = _load_data()

    status_filter = request.GET.get("status", "all").strip().lower()
    query = request.GET.get("q", "").strip().lower()

    filtered = all_items
    if status_filter == "active":
        filtered = [w for w in filtered if not w.is_cancelled]
    elif status_filter == "cancelled":
        filtered = [w for w in filtered if w.is_cancelled]

    if query:
        filtered = [
            w for w in filtered
            if query in w.teacher.name.lower()
            or query in w.discipline.name.lower()
        ]

    count_all = len(all_items)
    count_act = sum(1 for w in all_items if not w.is_cancelled)
    count_can = sum(1 for w in all_items if w.is_cancelled)

    context = {
        "workloads": filtered,
        "count_all": count_all,
        "count_act": count_act,
        "count_can": count_can,
        "status_filter": status_filter,
        "query": request.GET.get("q", ""),
    }
    return render(
        request,
        "workloads/workload_list.html",
        context,
    )


def workload_detail(request: HttpRequest, workload_id: int) -> HttpResponse:
    """Отобразить детальную информацию об учебном поручении."""
    _, _, workloads_list, _ = _load_data()
    workload = find_workload_by_id(workloads_list, workload_id)

    if not workload:
        return render(
            request,
            "workloads/workload_detail.html",
            {"workload": None},
            status=404,
        )

    context = {
        "workload": workload,
    }
    return render(
        request,
        "workloads/workload_detail.html",
        context,
        status=200,
    )


def workload_toggle(request: HttpRequest, workload_id: int) -> HttpResponse:
    """Изменить статус активности поручения (отмена / восстановление)."""
    _, _, workloads_list, w_path = _load_data()
    workload = find_workload_by_id(workloads_list, workload_id)
    if not workload:
        return render(
            request,
            "workloads/workload_detail.html",
            {"workload": None},
            status=404,
        )

    if workload.is_cancelled:
        workload.restore()
    else:
        workload.cancel()

    save_workloads(w_path, workloads_list)

    # Синхронизация с базой данных SQLite
    conn = get_connection()
    conn.execute(
        "UPDATE workloads SET is_cancelled = ? WHERE id = ?",
        [1 if workload.is_cancelled else 0, workload.id],
    )
    conn.commit()
    conn.close()

    next_url = request.GET.get("next", f"/workloads/{workload_id}/")
    return HttpResponseRedirect(next_url)


def statistics(request: HttpRequest) -> HttpResponse:
    """Сводная статистика нагрузки кафедры из SQLite (GROUP BY / HAVING)."""
    conn = get_connection()
    summary = conn.execute(
        """
        SELECT
            COUNT(DISTINCT w.id) AS total_workloads,
            COUNT(DISTINCT w.teacher_id) AS active_teachers,
            COALESCE(SUM(w.total_hours), 0.0) AS sum_hours,
            COALESCE(AVG(w.total_hours), 0.0) AS avg_hours
        FROM workloads w
        WHERE w.is_cancelled = 0;
        """
    ).fetchone()

    teachers_stats = conn.execute(
        """
        SELECT
            t.id,
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
        """
    ).fetchall()

    semester_stats = conn.execute(
        """
        SELECT
            d.semester,
            COUNT(w.id) AS assignments_count,
            COALESCE(SUM(w.total_hours), 0.0) AS semester_hours
        FROM workloads w
        JOIN disciplines d ON w.discipline_id = d.id
        WHERE w.is_cancelled = 0
        GROUP BY d.semester
        ORDER BY d.semester ASC;
        """
    ).fetchall()
    conn.close()

    context = {
        "summary": summary,
        "teachers_stats": teachers_stats,
        "semester_stats": semester_stats,
    }
    return render(request, "workloads/statistics.html", context)
