"""
Представления для приложения teachers.
"""

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from homepage.views import page, page_not_found
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

    teachers = load_teachers(t_path)
    disciplines = load_disciplines(d_path)
    workloads = load_workloads(w_path, teachers, disciplines)
    return teachers, disciplines, workloads


def _compliance_badge(status: str) -> str:
    """Вернуть HTML-бейдж статуса соответствия нагрузки."""
    if "Соответствует" in status:
        return f'<span class="badge bg-success">{status}</span>'
    if "Недогрузка" in status:
        return f'<span class="badge bg-warning text-dark">{status}</span>'
    return f'<span class="badge bg-danger">{status}</span>'


def teachers(request: HttpRequest) -> HttpResponse:
    """Отобразить список преподавателей с фильтрацией и поиском."""
    teachers_list, _, workloads = _load_data()

    query = request.GET.get("q", "").strip().lower()
    comp_filter = request.GET.get("compliance", "all").strip().lower()

    filtered_teachers = teachers_list
    if query:
        filtered_teachers = [
            t for t in filtered_teachers
            if query in t.name.lower() or query in t.department.lower()
        ]

    rows = []
    count_norm = 0
    count_under = 0
    count_over = 0

    for t in teachers_list:
        total = get_teacher_total_hours(workloads, t.id)
        norm = t.calculate_planned_hours()
        comp = check_workload_compliance(total, norm)
        if "Соответствует" in comp:
            count_norm += 1
        elif "Недогрузка" in comp:
            count_under += 1
        else:
            count_over += 1

    for t in filtered_teachers:
        total = get_teacher_total_hours(workloads, t.id)
        norm = t.calculate_planned_hours()
        comp = check_workload_compliance(total, norm)

        if comp_filter == "norm" and "Соответствует" not in comp:
            continue
        if comp_filter == "underload" and "Недогрузка" not in comp:
            continue
        if comp_filter == "overload" and "Перегрузка" not in comp:
            continue

        badge = _compliance_badge(comp)
        pct = calculate_plan_fulfillment_percent(total, norm)
        rows.append(f"""
        <tr>
          <td class="text-center">{t.id}</td>
          <td>
            <a href="/teachers/{t.id}/" class="fw-bold text-decoration-none">
              {t.name}
            </a>
          </td>
          <td>{t.position}</td>
          <td>{t.department}</td>
          <td class="text-center">{t.rate:.2f}</td>
          <td class="text-end">
            <div>{total:.1f} / {norm:.1f} ч</div>
            <div class="small text-muted">{pct:.1f}%</div>
          </td>
          <td class="text-center">{badge}</td>
          <td class="text-center">
            <a href="/teachers/{t.id}/"
               class="btn btn-sm btn-outline-primary">
              Карточка
            </a>
          </td>
        </tr>
        """)

    table_rows = "".join(rows) if rows else """
    <tr><td colspan="8" class="text-center py-4 text-muted">
      Преподаватели по заданным критериям не найдены
    </td></tr>
    """

    content = f"""
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h2 class="h3 fw-bold mb-0">Преподаватели кафедры</h2>
        <div class="text-muted small">
          Штатный состав и учет выполнения годовых норм
        </div>
      </div>
      <div>
        <a href="/teachers/add/" class="btn btn-success btn-sm me-2">
          <span class="fw-bold">+</span> Добавить преподавателя
        </a>
        <div class="btn-group">
          <a href="/teachers/?compliance=all"
             class="btn btn-outline-secondary btn-sm
             {'active' if comp_filter == 'all' else ''}">
            Все ({len(teachers_list)})
          </a>
          <a href="/teachers/?compliance=norm"
             class="btn btn-outline-success btn-sm
             {'active' if comp_filter == 'norm' else ''}">
            В норме ({count_norm})
          </a>
          <a href="/teachers/?compliance=underload"
             class="btn btn-outline-warning btn-sm
             {'active' if comp_filter == 'underload' else ''}">
            Недогрузка ({count_under})
          </a>
          <a href="/teachers/?compliance=overload"
             class="btn btn-outline-danger btn-sm
             {'active' if comp_filter == 'overload' else ''}">
            Перегрузка ({count_over})
          </a>
        </div>
      </div>
    </div>

    <form method="get" action="/teachers/" class="row g-2 mb-3">
      <div class="col-md-5">
        <input type="text" name="q" value="{query}"
               class="form-control form-control-sm"
               placeholder="Поиск по ФИО преподавателя или кафедре...">
      </div>
      <div class="col-auto">
        <button type="submit" class="btn btn-primary btn-sm">Найти</button>
        <a href="/teachers/" class="btn btn-outline-secondary btn-sm">
          Сброс
        </a>
      </div>
    </form>

    <div class="card shadow-sm border-0">
      <div class="table-responsive">
        <table class="table table-hover table-striped align-middle mb-0">
          <thead class="table-dark">
            <tr>
              <th class="text-center" style="width: 45px;">ID</th>
              <th>ФИО преподавателя</th>
              <th>Должность</th>
              <th>Кафедра</th>
              <th class="text-center">Ставка</th>
              <th class="text-end">Факт / План</th>
              <th class="text-center">Статус нормы</th>
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
    return HttpResponse(page("Список преподавателей", content))


def teacher_detail(request: HttpRequest, teacher_id: int) -> HttpResponse:
    """Отобразить детальную карточку нагрузки с прогресс-баром."""
    teachers_list, _, workloads = _load_data()
    teacher = find_teacher_by_id(teachers_list, teacher_id)
    if not teacher:
        return page_not_found(request)

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
    badge = _compliance_badge(compliance)

    bar_color = "bg-success"
    if "Недогрузка" in compliance:
        bar_color = "bg-warning"
    elif "Перегрузка" in compliance:
        bar_color = "bg-danger"

    diff_hours = total_hours - planned_hours
    if diff_hours >= 0:
        diff_sign = f"+{diff_hours:.1f}"
    else:
        diff_sign = f"{diff_hours:.1f}"

    w_rows = []
    for w in t_workloads:
        w_status = (
            '<span class="badge bg-secondary">Отменено</span>'
            if w.is_cancelled
            else '<span class="badge bg-success">Активно</span>'
        )
        toggle_link = (
            f"/workloads/{w.id}/toggle/?next=/teachers/{teacher.id}/"
        )
        toggle_btn = (
            f'<a href="{toggle_link}" '
            f'class="btn btn-sm btn-outline-success">Восстановить</a>'
            if w.is_cancelled
            else f'<a href="{toggle_link}" '
            f'class="btn btn-sm btn-outline-danger">Отменить</a>'
        )
        w_rows.append(f"""
        <tr class="{'table-light text-muted' if w.is_cancelled else ''}">
          <td class="text-center">
            <a href="/workloads/{w.id}/" class="text-decoration-none">
              #{w.id}
            </a>
          </td>
          <td>
            <a href="/workloads/{w.id}/" class="fw-semibold">
              {w.discipline.name}
            </a>
            <div class="small text-muted">
              Семестр {w.discipline.semester}
            </div>
          </td>
          <td class="text-center">{w.lectures:.1f}</td>
          <td class="text-center">{w.practices:.1f}</td>
          <td class="text-center">{w.labs:.1f}</td>
          <td class="text-center">{w.exams:.1f}</td>
          <td class="text-end fw-bold">{w.total_hours:.1f} ч</td>
          <td class="text-center">{w_status}</td>
          <td class="text-center">
            <div class="btn-group btn-group-sm">
              <a href="/workloads/{w.id}/"
                 class="btn btn-outline-primary">Инфо</a>
              {toggle_btn}
            </div>
          </td>
        </tr>
        """)

    workloads_table = "".join(w_rows) if w_rows else """
    <tr>
      <td colspan="9" class="text-center py-3 text-muted">
        Учебные поручения не закреплены
      </td>
    </tr>
    """

    content = f"""
    <div class="mb-3">
      <a href="/teachers/" class="btn btn-outline-secondary btn-sm">
        &larr; Назад к списку преподавателей
      </a>
    </div>

    <div class="card shadow-sm border-0 mb-4">
      <div class="card-header bg-dark text-white py-3">
        <h3 class="h4 mb-0 fw-bold">{teacher.name}</h3>
        <div class="small text-light opacity-75">
          {teacher.position} &bull; Кафедра: {teacher.department}
        </div>
      </div>
      <div class="card-body">
        <div class="row g-3 text-center text-md-start">
          <div class="col-md-3 col-6">
            <div class="text-muted small">Ставка по договору</div>
            <div class="fs-4 fw-bold">{teacher.rate:.2f} ст.</div>
          </div>
          <div class="col-md-3 col-6">
            <div class="text-muted small">Годовая норма</div>
            <div class="fs-4 fw-bold">{planned_hours:.1f} ч</div>
          </div>
          <div class="col-md-3 col-6">
            <div class="text-muted small">Фактическая нагрузка</div>
            <div class="fs-4 fw-bold text-primary">
              {total_hours:.1f} ч
            </div>
          </div>
          <div class="col-md-3 col-6">
            <div class="text-muted small">Фактическая ставка</div>
            <div class="fs-4 fw-bold">{actual_rate:.2f} ст.</div>
          </div>
        </div>

        <hr>

        <div class="mb-2 d-flex justify-content-between align-items-center">
          <span class="fw-bold small text-muted">
            Выполнение индивидуального плана ({fulfillment:.1f}%):
          </span>
          <span class="small text-muted">
            Отклонение от нормы: <strong>{diff_sign} ч</strong>
          </span>
        </div>
        <div class="progress mb-3" style="height: 22px;">
          <div class="progress-bar {bar_color} progress-bar-striped"
               role="progressbar"
               style="width: {min(fulfillment, 100):.1f}%;">
            {fulfillment:.1f}%
          </div>
        </div>

        <div class="d-flex justify-content-between align-items-center">
          <span class="text-muted small">
            Статус соответствия норме нагрузки:
          </span>
          <div>{badge}</div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-header bg-white py-3
                  d-flex justify-content-between align-items-center">
        <h4 class="h5 mb-0 fw-bold">Закрепленные учебные поручения</h4>
        <span class="badge bg-secondary">
          Всего поручений: {len(t_workloads)}
        </span>
      </div>
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th class="text-center" style="width: 50px;">ID</th>
              <th>Дисциплина</th>
              <th class="text-center">Лек.</th>
              <th class="text-center">Прак.</th>
              <th class="text-center">Лаб.</th>
              <th class="text-center">Экз.</th>
              <th class="text-end">Итого</th>
              <th class="text-center">Статус</th>
              <th class="text-center" style="width: 170px;">Действие</th>
            </tr>
          </thead>
          <tbody>
            {workloads_table}
          </tbody>
        </table>
      </div>
    </div>
    """
    return HttpResponse(page(f"Преподаватель: {teacher.name}", content))


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

    error_alert = (
        f'<div class="alert alert-danger shadow-sm mb-4">{error}</div>'
        if error
        else ""
    )

    positions = ["Профессор", "Доцент", "Старший преподаватель", "Ассистент"]
    opts = []
    for p in positions:
        sel = "selected" if p == position else ""
        opts.append(f'<option value="{p}" {sel}>{p}</option>')
    pos_options = "".join(opts)

    content = f"""
    <div class="row justify-content-center">
      <div class="col-md-7">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h2 class="h3 fw-bold mb-0">Добавление преподавателя</h2>
          <a href="/teachers/" class="btn btn-outline-secondary btn-sm">
            ← Назад к списку
          </a>
        </div>

        {error_alert}

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <form method="post" action="/teachers/add/">
              <div class="mb-3">
                <label for="name" class="form-label fw-bold">
                  ФИО преподавателя <span class="text-danger">*</span>
                </label>
                <input type="text" class="form-control" id="name" name="name"
                       value="{name}" placeholder="например: Смирнов А. П."
                       required autofocus>
              </div>

              <div class="mb-3">
                <label for="position" class="form-label fw-bold">
                  Должность <span class="text-danger">*</span>
                </label>
                <select class="form-select" id="position" name="position">
                  {pos_options}
                </select>
              </div>

              <div class="mb-3">
                <label for="department" class="form-label fw-bold">
                  Кафедра <span class="text-danger">*</span>
                </label>
                <input type="text" class="form-control" id="department"
                       name="department" value="{department}" required>
              </div>

              <div class="mb-4">
                <label for="rate" class="form-label fw-bold">
                  Доля ставки по договору (0.1 - 2.0)
                  <span class="text-danger">*</span>
                </label>
                <input type="number" class="form-control" id="rate" name="rate"
                       step="0.05" min="0.1" max="2.0" value="{rate_str}"
                       required>
                <div class="form-text">
                  При ставке 1.0 норма составляет 900.0 часов в год.
                </div>
              </div>

              <div class="d-flex gap-2 justify-content-end">
                <a href="/teachers/"
                   class="btn btn-outline-secondary">Отмена</a>
                <button type="submit" class="btn btn-success px-4">
                  Сохранить преподавателя
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    """
    return HttpResponse(page("Добавление преподавателя", content))
