"""
Представления для приложения teachers.
"""

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from homepage.views import page, page_not_found
from models.teachers import find_teacher_by_id
from models.workloads import (
    calculate_actual_rate,
    calculate_plan_fulfillment_percent,
    check_workload_compliance,
    get_teacher_total_hours,
    get_teacher_workloads,
)
from storage import load_disciplines, load_teachers, load_workloads


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
    """Отобразить список преподавателей кафедры."""
    teachers_list, _, workloads = _load_data()

    rows = []
    for t in teachers_list:
        total = get_teacher_total_hours(workloads, t.id)
        norm = t.calculate_planned_hours()
        comp = check_workload_compliance(total, norm)
        badge = _compliance_badge(comp)
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
          <td class="text-end">{total:.1f} / {norm:.1f} ч</td>
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
    <tr><td colspan="8" class="text-center py-4">Список пуст</td></tr>
    """

    content = f"""
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2 class="h3 fw-bold mb-0">Преподаватели кафедры</h2>
      <span class="badge bg-primary fs-6">
        Всего: {len(teachers_list)}
      </span>
    </div>

    <div class="card shadow-sm border-0">
      <div class="table-responsive">
        <table class="table table-hover table-striped align-middle mb-0">
          <thead class="table-dark">
            <tr>
              <th class="text-center" style="width: 50px;">ID</th>
              <th>ФИО преподавателя</th>
              <th>Должность</th>
              <th>Кафедра</th>
              <th class="text-center">Ставка</th>
              <th class="text-end">Факт / План</th>
              <th class="text-center">Статус нормы</th>
              <th class="text-center" style="width: 120px;">Действие</th>
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
    """Отобразить детальную карточку нагрузки преподавателя."""
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

    w_rows = []
    for w in t_workloads:
        w_status = (
            '<span class="badge bg-secondary">Отменено</span>'
            if w.is_cancelled
            else '<span class="badge bg-success">Активно</span>'
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
        </tr>
        """)

    workloads_table = "".join(w_rows) if w_rows else """
    <tr>
      <td colspan="8" class="text-center py-3 text-muted">
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
        <div class="row g-3">
          <div class="col-md-3 col-6">
            <div class="text-muted small">Ставка по договору</div>
            <div class="fs-5 fw-bold">{teacher.rate:.2f} ст.</div>
          </div>
          <div class="col-md-3 col-6">
            <div class="text-muted small">Норма часов в год</div>
            <div class="fs-5 fw-bold">{planned_hours:.1f} ч</div>
          </div>
          <div class="col-md-3 col-6">
            <div class="text-muted small">Фактическая нагрузка</div>
            <div class="fs-5 fw-bold text-primary">
              {total_hours:.1f} ч
            </div>
          </div>
          <div class="col-md-3 col-6">
            <div class="text-muted small">Фактическая ставка</div>
            <div class="fs-5 fw-bold">{actual_rate:.2f} ст.</div>
          </div>
        </div>

        <hr>

        <div class="d-flex align-items-center gap-3">
          <div>
            <span class="text-muted small d-block">
              Выполнение плана:
            </span>
            <span class="fs-5 fw-bold">{fulfillment:.1f} %</span>
          </div>
          <div class="ms-auto text-end">
            <span class="text-muted small d-block">
              Статус проверки нагрузки:
            </span>
            <div class="mt-1">{badge}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="card shadow-sm border-0">
      <div class="card-header bg-white py-3">
        <h4 class="h5 mb-0 fw-bold">Закрепленные учебные поручения</h4>
      </div>
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-light">
            <tr>
              <th class="text-center" style="width: 60px;">ID</th>
              <th>Дисциплина</th>
              <th class="text-center">Лек.</th>
              <th class="text-center">Прак.</th>
              <th class="text-center">Лаб.</th>
              <th class="text-center">Экз.</th>
              <th class="text-end">Итого</th>
              <th class="text-center">Статус</th>
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
