"""
Представления для приложения workloads.
"""

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
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
    next_url = request.GET.get("next", f"/workloads/{workload_id}/")
    return HttpResponseRedirect(next_url)
