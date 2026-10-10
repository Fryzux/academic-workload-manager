"""
Представления для приложения workloads.
"""

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from homepage.views import page, page_not_found
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

    rows = []
    for w in filtered:
        status_badge = (
            '<span class="badge bg-secondary">Отменено</span>'
            if w.is_cancelled
            else '<span class="badge bg-success">Активно</span>'
        )
        toggle_btn = (
            f'<a href="/workloads/{w.id}/toggle/?next=/workloads/" '
            f'class="btn btn-sm btn-outline-success">Восстановить</a>'
            if w.is_cancelled
            else f'<a href="/workloads/{w.id}/toggle/?next=/workloads/" '
            f'class="btn btn-sm btn-outline-warning">Отменить</a>'
        )
        row_cls = "table-light text-muted" if w.is_cancelled else ""
        rows.append(f"""
        <tr class="{row_cls}">
          <td class="text-center">{w.id}</td>
          <td>
            <a href="/teachers/{w.teacher.id}/"
               class="fw-bold text-decoration-none">
              {w.teacher.name}
            </a>
          </td>
          <td>
            <a href="/workloads/{w.id}/" class="text-decoration-none">
              {w.discipline.name}
            </a>
          </td>
          <td class="text-center">{w.discipline.semester}</td>
          <td class="text-center">{w.lectures:.1f}</td>
          <td class="text-center">{w.practices:.1f}</td>
          <td class="text-center">{w.labs:.1f}</td>
          <td class="text-center">{w.exams:.1f}</td>
          <td class="text-end fw-bold">{w.total_hours:.1f} ч</td>
          <td class="text-center">{status_badge}</td>
          <td class="text-center">
            <div class="btn-group btn-group-sm">
              <a href="/workloads/{w.id}/"
                 class="btn btn-outline-primary">Инфо</a>
              {toggle_btn}
            </div>
          </td>
        </tr>
        """)

    table_rows = "".join(rows) if rows else """
    <tr><td colspan="11" class="text-center py-4 text-muted">
      Поручения по заданным критериям не найдены
    </td></tr>
    """

    content = f"""
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h2 class="h3 fw-bold mb-0">Учебные поручения</h2>
        <div class="text-muted small">
          Журнал распределения академических часов кафедры
        </div>
      </div>
      <div class="btn-group">
        <a href="/workloads/?status=all"
           class="btn btn-outline-secondary btn-sm
           {'active' if status_filter == 'all' else ''}">
          Все ({count_all})
        </a>
        <a href="/workloads/?status=active"
           class="btn btn-outline-success btn-sm
           {'active' if status_filter == 'active' else ''}">
          Активные ({count_act})
        </a>
        <a href="/workloads/?status=cancelled"
           class="btn btn-outline-danger btn-sm
           {'active' if status_filter == 'cancelled' else ''}">
          Отмененные ({count_can})
        </a>
      </div>
    </div>

    <form method="get" action="/workloads/" class="row g-2 mb-3">
      <div class="col-md-5">
        <input type="text" name="q" value="{query}"
               class="form-control form-control-sm"
               placeholder="Поиск по преподавателю или дисциплине...">
      </div>
      <div class="col-auto">
        <button type="submit" class="btn btn-primary btn-sm">Найти</button>
        <a href="/workloads/" class="btn btn-outline-secondary btn-sm">
          Сброс
        </a>
      </div>
    </form>

    <div class="card shadow-sm border-0">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-dark">
            <tr>
              <th class="text-center" style="width: 45px;">ID</th>
              <th>Преподаватель</th>
              <th>Дисциплина</th>
              <th class="text-center">Сем.</th>
              <th class="text-center">Лек.</th>
              <th class="text-center">Прак.</th>
              <th class="text-center">Лаб.</th>
              <th class="text-center">Экз.</th>
              <th class="text-end">Итого</th>
              <th class="text-center">Статус</th>
              <th class="text-center" style="width: 170px;">Действия</th>
            </tr>
          </thead>
          <tbody>
            {table_rows}
          </tbody>
        </table>
      </div>
    </div>
    """
    return HttpResponse(page("Список учебных поручений", content))


def workload_detail(request: HttpRequest, workload_id: int) -> HttpResponse:
    """Отобразить детальную информацию об учебном поручении."""
    _, _, workloads_list, _ = _load_data()
    workload = find_workload_by_id(workloads_list, workload_id)
    if not workload:
        return page_not_found(request)

    status_badge = (
        '<span class="badge bg-secondary fs-6">Отменено</span>'
        if workload.is_cancelled
        else '<span class="badge bg-success fs-6">Активно</span>'
    )
    toggle_action_btn = (
        f'<a href="/workloads/{workload.id}/toggle/" '
        f'class="btn btn-success">'
        f'Восстановить поручение</a>'
        if workload.is_cancelled
        else f'<a href="/workloads/{workload.id}/toggle/" '
        f'class="btn btn-outline-danger">'
        f'Отменить поручение</a>'
    )

    content = f"""
    <div class="mb-3 d-flex justify-content-between">
      <a href="/workloads/" class="btn btn-outline-secondary btn-sm">
        &larr; Назад к списку поручений
      </a>
      <div>{toggle_action_btn}</div>
    </div>

    <div class="card shadow-sm border-0 mb-4">
      <div class="card-header bg-dark text-white py-3
                  d-flex justify-content-between align-items-center">
        <div>
          <h3 class="h4 mb-0 fw-bold">
            Поручение #{workload.id}: {workload.discipline.name}
          </h3>
          <div class="small text-light opacity-75">
            Семестр: {workload.discipline.semester}
          </div>
        </div>
        <div>{status_badge}</div>
      </div>
      <div class="card-body">
        <div class="row g-4">
          <div class="col-md-6">
            <h5 class="fw-bold text-secondary">Закрепленный преподаватель</h5>
            <div class="p-3 bg-light rounded border">
              <div class="fs-5 fw-bold">
                <a href="/teachers/{workload.teacher.id}/"
                   class="text-decoration-none">
                  {workload.teacher.name}
                </a>
              </div>
              <div class="text-muted small mt-1">
                {workload.teacher.position} &bull;
                Кафедра: {workload.teacher.department}
              </div>
              <div class="mt-2">
                <span class="badge bg-secondary">
                  Ставка: {workload.teacher.rate:.2f} ст.
                </span>
              </div>
              <div class="mt-3">
                <a href="/teachers/{workload.teacher.id}/"
                   class="btn btn-sm btn-outline-primary">
                  Перейти в карточку преподавателя &rarr;
                </a>
              </div>
            </div>
          </div>

          <div class="col-md-6">
            <h5 class="fw-bold text-secondary">Объем часов по видам</h5>
            <ul class="list-group list-group-flush border rounded">
              <li class="list-group-item d-flex justify-content-between">
                <span>Лекционные занятия:</span>
                <span class="fw-bold">{workload.lectures:.1f} ч</span>
              </li>
              <li class="list-group-item d-flex justify-content-between">
                <span>Практические занятия:</span>
                <span class="fw-bold">{workload.practices:.1f} ч</span>
              </li>
              <li class="list-group-item d-flex justify-content-between">
                <span>Лабораторные работы:</span>
                <span class="fw-bold">{workload.labs:.1f} ч</span>
              </li>
              <li class="list-group-item d-flex justify-content-between">
                <span>Прием зачетов / экзаменов:</span>
                <span class="fw-bold">{workload.exams:.1f} ч</span>
              </li>
              <li class="list-group-item d-flex justify-content-between
                         bg-light fw-bold fs-5 text-primary">
                <span>Итоговый объем:</span>
                <span>{workload.total_hours:.1f} ч</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    """
    return HttpResponse(
        page(f"Учебное поручение #{workload.id}", content)
    )


def workload_toggle(request: HttpRequest, workload_id: int) -> HttpResponse:
    """Изменить статус активности поручения (отмена / восстановление)."""
    _, _, workloads_list, w_path = _load_data()
    workload = find_workload_by_id(workloads_list, workload_id)
    if not workload:
        return page_not_found(request)

    if workload.is_cancelled:
        workload.restore()
    else:
        workload.cancel()

    save_workloads(w_path, workloads_list)
    next_url = request.GET.get("next", f"/workloads/{workload_id}/")
    return HttpResponseRedirect(next_url)
