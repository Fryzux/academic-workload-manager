"""
Представления для приложения homepage.
"""

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from models.workloads import get_teacher_total_hours
from storage import load_disciplines, load_teachers, load_workloads


def _load_stats():
    """Загрузить агрегированную статистику нагрузки кафедры."""
    base = settings.BASE_DIR
    t_path = str(base / "data" / "teachers.json")
    d_path = str(base / "data" / "disciplines.json")
    w_path = str(base / "data" / "workloads.json")

    teachers = load_teachers(t_path)
    disciplines = load_disciplines(d_path)
    workloads = load_workloads(w_path, teachers, disciplines)

    total_rate = sum(t.rate for t in teachers)
    active_workloads = [w for w in workloads if not w.is_cancelled]
    total_hours = sum(w.total_hours for w in active_workloads)
    total_lectures = sum(w.lectures for w in active_workloads)
    total_practices = sum(w.practices for w in active_workloads)
    total_labs = sum(w.labs for w in active_workloads)
    total_exams = sum(w.exams for w in active_workloads)

    norm_count = 0
    under_count = 0
    over_count = 0
    for t in teachers:
        t_hrs = get_teacher_total_hours(workloads, t.id)
        norm = t.calculate_planned_hours()
        lower = norm * 0.95
        upper = norm * 1.05
        if lower <= t_hrs <= upper:
            norm_count += 1
        elif t_hrs < lower:
            under_count += 1
        else:
            over_count += 1

    return {
        "teachers_count": len(teachers),
        "disciplines_count": len(disciplines),
        "workloads_count": len(workloads),
        "active_workloads_count": len(active_workloads),
        "total_rate": total_rate,
        "total_hours": total_hours,
        "total_lectures": total_lectures,
        "total_practices": total_practices,
        "total_labs": total_labs,
        "total_exams": total_exams,
        "norm_count": norm_count,
        "under_count": under_count,
        "over_count": over_count,
    }


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница со сводной аналитической панелью кафедры."""
    stats = _load_stats()
    return render(
        request,
        "homepage/index.html",
        {"stats": stats},
    )


def page_not_found(request: HttpRequest, exception=None) -> HttpResponse:
    """Пользовательская страница ошибки 404 (Не найдено)."""
    return render(
        request,
        "404.html",
        status=404,
    )
