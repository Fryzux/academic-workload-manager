"""
Представления для приложения teachers.
"""

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from models.teachers import add_teacher, find_teacher_by_id
from models.workloads import (
    calculate_actual_rate,
    calculate_plan_fulfillment_percent,
    check_workload_compliance,
    get_teacher_total_hours,
    get_teacher_workloads,
)
from storage import (
    load_disciplines,
    load_teachers,
    load_workloads,
    save_teachers,
)


def _load_data():
    """Загрузить данные преподавателей, дисциплин и поручений."""
    base = settings.BASE_DIR
    t_path = str(base / "data" / "teachers.json")
    d_path = str(base / "data" / "disciplines.json")
    w_path = str(base / "data" / "workloads.json")

    teachers_list = load_teachers(t_path)
    disciplines_list = load_disciplines(d_path)
    workloads_list = load_workloads(
        w_path, teachers_list, disciplines_list
    )
    return teachers_list, disciplines_list, workloads_list


def teachers(request: HttpRequest) -> HttpResponse:
    """Отобразить список преподавателей с фильтрацией и поиском."""
    teachers_list, _, workloads = _load_data()

    query = request.GET.get("q", "").strip().lower()
    comp_filter = request.GET.get("compliance", "all").strip().lower()

    count_norm = 0
    count_under = 0
    count_over = 0

    all_items = []
    for t in teachers_list:
        total = get_teacher_total_hours(workloads, t.id)
        norm = t.calculate_planned_hours()
        comp = check_workload_compliance(total, norm)
        if "Соответствует" in comp:
            count_norm += 1
            badge_cls = "bg-success"
        elif "Недогрузка" in comp:
            count_under += 1
            badge_cls = "bg-warning text-dark"
        else:
            count_over += 1
            badge_cls = "bg-danger"

        all_items.append({
            "teacher": t,
            "total": total,
            "norm": norm,
            "comp": comp,
            "badge_cls": badge_cls,
        })

    filtered_items = all_items
    if query:
        filtered_items = [
            item for item in filtered_items
            if query in item["teacher"].name.lower()
            or query in item["teacher"].department.lower()
        ]

    if comp_filter == "norm":
        filtered_items = [
            i for i in filtered_items if "Соответствует" in i["comp"]
        ]
    elif comp_filter == "underload":
        filtered_items = [
            i for i in filtered_items if "Недогрузка" in i["comp"]
        ]
    elif comp_filter == "overload":
        filtered_items = [
            i for i in filtered_items if "Перегрузка" in i["comp"]
        ]

    context = {
        "teacher_items": filtered_items,
        "total_count": len(teachers_list),
        "count_norm": count_norm,
        "count_under": count_under,
        "count_over": count_over,
        "query": request.GET.get("q", ""),
        "comp_filter": comp_filter,
    }
    return render(request, "teachers/teacher_list.html", context)


def teacher_detail(request: HttpRequest, teacher_id: int) -> HttpResponse:
    """Отобразить детальную карточку нагрузки с прогресс-баром."""
    teachers_list, _, workloads = _load_data()
    teacher = find_teacher_by_id(teachers_list, teacher_id)

    if not teacher:
        return render(
            request,
            "teachers/teacher_detail.html",
            {"teacher": None},
            status=404,
        )

    t_workloads = get_teacher_workloads(
        workloads, teacher.id, include_cancelled=True
    )
    total_hours = get_teacher_total_hours(workloads, teacher.id)
    planned_hours = teacher.calculate_planned_hours()
    compliance = check_workload_compliance(total_hours, planned_hours)
    actual_rate = calculate_actual_rate(total_hours)
    fulfillment = calculate_plan_fulfillment_percent(
        total_hours, planned_hours
    )

    bar_color = "bg-success"
    badge_cls = "bg-success"
    if "Недогрузка" in compliance:
        bar_color = "bg-warning"
        badge_cls = "bg-warning text-dark"
    elif "Перегрузка" in compliance:
        bar_color = "bg-danger"
        badge_cls = "bg-danger"

    diff_hours = total_hours - planned_hours
    if diff_hours >= 0:
        diff_sign = f"+{diff_hours:.1f}"
    else:
        diff_sign = f"{diff_hours:.1f}"

    context = {
        "teacher": teacher,
        "t_workloads": t_workloads,
        "total_hours": total_hours,
        "planned_hours": planned_hours,
        "compliance": compliance,
        "actual_rate": actual_rate,
        "fulfillment": fulfillment,
        "bar_color": bar_color,
        "badge_cls": badge_cls,
        "bar_width": min(fulfillment, 100),
        "diff_sign": diff_sign,
    }
    return render(
        request,
        "teachers/teacher_detail.html",
        context,
        status=200,
    )


@csrf_exempt
def teacher_add(request: HttpRequest) -> HttpResponse:
    """Форма и обработка добавления нового преподавателя."""
    error = ""
    name = ""
    position = "Доцент"
    department = "Индустриального программирования"
    rate_str = "1.0"

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        position = request.POST.get("position", "").strip()
        department = request.POST.get("department", "").strip()
        rate_str = request.POST.get("rate", "1.0").strip()

        if not name:
            error = "Укажите ФИО преподавателя."
        elif not position:
            error = "Укажите должность преподавателя."
        elif not department:
            error = "Укажите кафедру."
        else:
            try:
                rate_val = float(rate_str)
                if not (0.1 <= rate_val <= 2.0):
                    error = "Ставка должна быть в диапазоне от 0.1 до 2.0."
            except ValueError:
                error = "Некорректное числовое значение ставки."

        if not error:
            base = settings.BASE_DIR
            t_path = str(base / "data" / "teachers.json")
            teachers_list = load_teachers(t_path)
            new_teacher = add_teacher(
                teachers=teachers_list,
                name=name,
                position=position,
                department=department,
                rate=rate_val,
            )
            save_teachers(t_path, teachers_list)
            return HttpResponseRedirect(f"/teachers/{new_teacher.id}/")

    context = {
        "error": error,
        "name": name,
        "position": position,
        "department": department,
        "rate_str": rate_str,
    }
    return render(request, "teachers/teacher_form.html", context)
