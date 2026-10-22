"""
Представления для приложения disciplines.
"""

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from db.database import get_connection
from models.disciplines import add_discipline, find_discipline_by_id
from storage import (
    load_disciplines,
    load_teachers,
    load_workloads,
    save_disciplines,
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
    return teachers, disciplines, workloads, d_path


def disciplines_list(request: HttpRequest) -> HttpResponse:
    """Отобразить каталог учебных дисциплин кафедры."""
    _, disciplines, workloads, _ = _load_data()

    query = request.GET.get("q", "").strip().lower()
    sem_filter = request.GET.get("semester", "all").strip().lower()

    filtered = disciplines
    if query:
        filtered = [
            d for d in filtered
            if query in d.name.lower() or query in d.department.lower()
        ]

    if sem_filter != "all" and sem_filter.isdigit():
        filtered = [d for d in filtered if d.semester == int(sem_filter)]

    disc_items = []
    for d in filtered:
        d_workloads = [
            w for w in workloads
            if w.discipline.id == d.id and not w.is_cancelled
        ]
        hours = sum(w.total_hours for w in d_workloads)
        disc_items.append({
            "disc": d,
            "count": len(d_workloads),
            "hours": hours,
        })

    context = {
        "disc_items": disc_items,
        "query": request.GET.get("q", ""),
        "sem_filter": sem_filter,
    }
    return render(
        request,
        "disciplines/disciplines_list.html",
        context,
    )


def discipline_detail(
    request: HttpRequest,
    discipline_id: int,
) -> HttpResponse:
    """Отобразить карточку дисциплины и список поручений по ней."""
    _, disciplines, workloads, _ = _load_data()
    disc = find_discipline_by_id(disciplines, discipline_id)

    if not disc:
        return render(
            request,
            "disciplines/discipline_detail.html",
            {"disc": None},
            status=404,
        )

    d_workloads = [
        w for w in workloads
        if w.discipline.id == disc.id
    ]
    active_workloads = [w for w in d_workloads if not w.is_cancelled]
    total_hours = sum(w.total_hours for w in active_workloads)

    context = {
        "disc": disc,
        "d_workloads": d_workloads,
        "total_hours": total_hours,
    }
    return render(
        request,
        "disciplines/discipline_detail.html",
        context,
        status=200,
    )


@csrf_exempt
def discipline_add(request: HttpRequest) -> HttpResponse:
    """Форма и обработка добавления новой дисциплины."""
    error = ""
    name = ""
    department = "Индустриального программирования"
    semester_str = "1"

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        department = request.POST.get("department", "").strip()
        semester_str = request.POST.get("semester", "1").strip()

        if not name:
            error = "Укажите наименование дисциплины."
        elif not department:
            error = "Укажите кафедру."
        else:
            try:
                sem_val = int(semester_str)
                if not (1 <= sem_val <= 12):
                    error = (
                        "Номер семестра должен быть в диапазоне от 1 до 12."
                    )
            except ValueError:
                error = "Некорректное числовое значение семестра."

        if not error:
            base = settings.BASE_DIR
            d_path = str(base / "data" / "disciplines.json")
            disciplines_list_data = load_disciplines(d_path)
            new_disc = add_discipline(
                disciplines=disciplines_list_data,
                name=name,
                department=department,
                semester=sem_val,
            )
            save_disciplines(d_path, disciplines_list_data)

            # Синхронизация с базой SQLite
            conn = get_connection()
            conn.execute(
                """
                INSERT OR REPLACE INTO disciplines (
                    id, name, department, semester
                ) VALUES (?, ?, ?, ?)
                """,
                [
                    new_disc.id,
                    new_disc.name,
                    new_disc.department,
                    new_disc.semester,
                ],
            )
            conn.commit()
            conn.close()

            return HttpResponseRedirect(f"/disciplines/{new_disc.id}/")

    context = {
        "error": error,
        "name": name,
        "department": department,
        "semester_str": semester_str,
    }
    return render(
        request,
        "disciplines/discipline_form.html",
        context,
    )


def available_disciplines(request: HttpRequest) -> HttpResponse:
    """Поиск нераспределенных дисциплин по семестру (подзапрос NOT IN)."""
    semester = request.GET.get("semester", "").strip()
    conn = get_connection()
    if semester and semester.isdigit():
        disciplines_data = conn.execute(
            """
            SELECT id, name, department, semester
            FROM disciplines
            WHERE id NOT IN (
                SELECT discipline_id
                FROM workloads
                WHERE is_cancelled = 0
            ) AND semester = ?
            ORDER BY semester ASC, name ASC;
            """,
            [int(semester)],
        ).fetchall()
    else:
        disciplines_data = conn.execute(
            """
            SELECT id, name, department, semester
            FROM disciplines
            WHERE id NOT IN (
                SELECT discipline_id
                FROM workloads
                WHERE is_cancelled = 0
            )
            ORDER BY semester ASC, name ASC;
            """
        ).fetchall()
    conn.close()
    return render(
        request,
        "disciplines/available.html",
        {
            "disciplines": disciplines_data,
            "semester": semester,
        },
    )
