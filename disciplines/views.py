"""
Представления для приложения disciplines.
"""

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from homepage.views import page, page_not_found
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
    teachers, disciplines, workloads, _ = _load_data()

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

    rows = []
    for d in filtered:
        d_workloads = [
            w for w in workloads
            if w.discipline.id == d.id and not w.is_cancelled
        ]
        total_hours = sum(w.total_hours for w in d_workloads)
        teachers_count = len({w.teacher.id for w in d_workloads})

        rows.append(f"""
        <tr>
          <td class="text-center">{d.id}</td>
          <td>
            <a href="/disciplines/{d.id}/"
               class="fw-bold text-decoration-none">
              {d.name}
            </a>
          </td>
          <td>{d.department}</td>
          <td class="text-center">
            <span class="badge bg-info text-dark">сем. {d.semester}</span>
          </td>
          <td class="text-center">{len(d_workloads)}</td>
          <td class="text-center">{teachers_count}</td>
          <td class="text-end fw-bold">{total_hours:.1f} ч</td>
          <td class="text-center">
            <a href="/disciplines/{d.id}/"
               class="btn btn-sm btn-outline-primary">Карточка</a>
          </td>
        </tr>
        """)

    table_rows = "".join(rows) if rows else """
    <tr><td colspan="8" class="text-center py-4 text-muted">
      Дисциплины по заданным критериям не найдены
    </td></tr>
    """

    content = f"""
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h2 class="h3 fw-bold mb-0">Учебные предметы и дисциплины</h2>
        <div class="text-muted small">
          Реестр дисциплин, семестров и распределенных часов
        </div>
      </div>
      <a href="/disciplines/add/" class="btn btn-success btn-sm">
        <span class="fw-bold">+</span> Добавить предмет
      </a>
    </div>

    <form method="get" action="/disciplines/" class="row g-2 mb-3">
      <div class="col-md-6">
        <input type="text" name="q" value="{query}"
               class="form-control form-control-sm"
               placeholder="Поиск по названию предмета или кафедре...">
      </div>
      <div class="col-auto">
        <button type="submit" class="btn btn-primary btn-sm">Найти</button>
        <a href="/disciplines/" class="btn btn-outline-secondary btn-sm">
          Сброс
        </a>
      </div>
    </form>

    <div class="card shadow-sm border-0">
      <div class="table-responsive">
        <table class="table table-hover table-striped align-middle mb-0">
          <thead class="table-dark">
            <tr>
              <th class="text-center" style="width: 50px;">ID</th>
              <th>Название предмета</th>
              <th>Кафедра</th>
              <th class="text-center">Семестр</th>
              <th class="text-center">Поручений</th>
              <th class="text-center">Преподавателей</th>
              <th class="text-end">Всего часов</th>
              <th class="text-center" style="width: 110px;">Действие</th>
            </tr>
          </thead>
          <tbody>
            {table_rows}
          </tbody>
        </table>
      </div>
    </div>
    """
    return HttpResponse(page("Список дисциплин", content))


@csrf_exempt
def discipline_add(request: HttpRequest) -> HttpResponse:
    """Форма и обработка создания новой учебной дисциплины."""
    error = ""
    name = ""
    department = "Индустриального программирования"
    semester_val = 1

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        department = request.POST.get("department", "").strip()
        sem_str = request.POST.get("semester", "1").strip()

        if not name:
            error = "Укажите название учебной дисциплины."
        elif not department:
            error = "Укажите кафедру."
        else:
            try:
                semester_val = int(sem_str)
                if not (1 <= semester_val <= 12):
                    error = "Семестр должен быть от 1 до 12."
            except ValueError:
                error = "Некорректный номер семестра."

        if not error:
            teachers, disciplines, workloads, d_path = _load_data()
            new_d = add_discipline(
                disciplines=disciplines,
                name=name,
                department=department,
                semester=semester_val,
            )
            save_disciplines(d_path, disciplines)
            return HttpResponseRedirect(f"/disciplines/{new_d.id}/")

    error_alert = (
        f'<div class="alert alert-danger shadow-sm mb-4">{error}</div>'
        if error
        else ""
    )

    sem_opts = []
    for s in range(1, 13):
        sel = "selected" if s == semester_val else ""
        sem_opts.append(f'<option value="{s}" {sel}>{s} семестр</option>')
    sem_options = "".join(sem_opts)

    content = f"""
    <div class="row justify-content-center">
      <div class="col-md-7">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h2 class="h3 fw-bold mb-0">Добавление предмета (дисциплины)</h2>
          <a href="/disciplines/" class="btn btn-outline-secondary btn-sm">
            ← Назад к списку
          </a>
        </div>

        {error_alert}

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <form method="post" action="/disciplines/add/">
              <div class="mb-3">
                <label for="name" class="form-label fw-bold">
                  Название дисциплины <span class="text-danger">*</span>
                </label>
                <input type="text" class="form-control" id="name" name="name"
                       value="{name}"
                       placeholder="например: Технологии машинного обучения"
                       required autofocus>
              </div>

              <div class="mb-3">
                <label for="department" class="form-label fw-bold">
                  Кафедра <span class="text-danger">*</span>
                </label>
                <input type="text" class="form-control" id="department"
                       name="department" value="{department}" required>
              </div>

              <div class="mb-4">
                <label for="semester" class="form-label fw-bold">
                  Учебный семестр (1 - 12) <span class="text-danger">*</span>
                </label>
                <select class="form-select" id="semester" name="semester">
                  {sem_options}
                </select>
                <div class="form-text">
                  Семестр определяет распределение нагрузки в учебном плане.
                </div>
              </div>

              <div class="d-flex gap-2 justify-content-end">
                <a href="/disciplines/"
                   class="btn btn-outline-secondary">Отмена</a>
                <button type="submit" class="btn btn-success px-4">
                  Сохранить предмет
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    """
    return HttpResponse(page("Добавление дисциплины", content))


def discipline_detail(
    request: HttpRequest,
    discipline_id: int,
) -> HttpResponse:
    """Отобразить детальную информацию о дисциплине."""
    teachers, disciplines, workloads, _ = _load_data()
    discipline = find_discipline_by_id(disciplines, discipline_id)
    if not discipline:
        return page_not_found(request)

    d_workloads = [
        w for w in workloads
        if w.discipline.id == discipline.id
    ]

    total_lectures = sum(
        w.lectures for w in d_workloads if not w.is_cancelled
    )
    total_practices = sum(
        w.practices for w in d_workloads if not w.is_cancelled
    )
    total_labs = sum(w.labs for w in d_workloads if not w.is_cancelled)
    total_hours = sum(
        w.total_hours for w in d_workloads if not w.is_cancelled
    )

    rows = []
    for w in d_workloads:
        st_badge = (
            '<span class="badge bg-secondary">Отменено</span>'
            if w.is_cancelled
            else '<span class="badge bg-success">Активно</span>'
        )
        rows.append(f"""
        <tr>
          <td class="text-center">{w.id}</td>
          <td>
            <a href="/teachers/{w.teacher.id}/"
               class="fw-bold text-decoration-none">
              {w.teacher.name}
            </a>
            <div class="small text-muted">{w.teacher.position}</div>
          </td>
          <td class="text-center">{w.lectures:.1f}</td>
          <td class="text-center">{w.practices:.1f}</td>
          <td class="text-center">{w.labs:.1f}</td>
          <td class="text-center">{w.exams:.1f}</td>
          <td class="text-end fw-bold">{w.total_hours:.1f} ч</td>
          <td class="text-center">{st_badge}</td>
          <td class="text-center">
            <a href="/workloads/{w.id}/"
               class="btn btn-sm btn-outline-primary">Инфо</a>
          </td>
        </tr>
        """)

    table_rows = "".join(rows) if rows else """
    <tr><td colspan="9" class="text-center py-4 text-muted">
      За этой дисциплиной пока не закреплено ни одного поручения
    </td></tr>
    """

    content = f"""
    <div class="mb-4">
      <a href="/disciplines/" class="btn btn-outline-secondary btn-sm mb-3">
        ← Ко всем дисциплинам
      </a>
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <span class="badge bg-primary mb-1">
            Семестр {discipline.semester}
          </span>
          <h2 class="h3 fw-bold mb-0">{discipline.name}</h2>
          <div class="text-muted">Кафедра: {discipline.department}</div>
        </div>
        <span class="badge bg-light text-dark border p-2 fs-6">
          ID дисциплины: {discipline.id}
        </span>
      </div>
    </div>

    <div class="row g-3 mb-4">
      <div class="col-md-3 col-6">
        <div class="card shadow-sm border-0 text-center p-3">
          <div class="text-muted small">Лекции</div>
          <div class="fs-4 fw-bold">{total_lectures:.1f} ч</div>
        </div>
      </div>
      <div class="col-md-3 col-6">
        <div class="card shadow-sm border-0 text-center p-3">
          <div class="text-muted small">Практики</div>
          <div class="fs-4 fw-bold">{total_practices:.1f} ч</div>
        </div>
      </div>
      <div class="col-md-3 col-6">
        <div class="card shadow-sm border-0 text-center p-3">
          <div class="text-muted small">Лабораторные</div>
          <div class="fs-4 fw-bold">{total_labs:.1f} ч</div>
        </div>
      </div>
      <div class="col-md-3 col-6">
        <div class="card shadow-sm border-0 text-center p-3">
          <div class="text-muted small">Всего по предмету</div>
          <div class="fs-4 fw-bold text-primary">{total_hours:.1f} ч</div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-header bg-white py-3">
        <h5 class="mb-0 fw-bold">Преподаватели, ведущие данный предмет</h5>
      </div>
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th class="text-center" style="width: 50px;">ID</th>
              <th>Преподаватель</th>
              <th class="text-center">Лек.</th>
              <th class="text-center">Прак.</th>
              <th class="text-center">Лаб.</th>
              <th class="text-center">Экз.</th>
              <th class="text-end">Итого</th>
              <th class="text-center">Статус</th>
              <th class="text-center" style="width: 100px;">Действие</th>
            </tr>
          </thead>
          <tbody>
            {table_rows}
          </tbody>
        </table>
      </div>
    </div>
    """
    return HttpResponse(page(f"Предмет: {discipline.name}", content))
