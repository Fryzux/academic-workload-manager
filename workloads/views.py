"""
Представления для приложения workloads.
"""

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from homepage.views import page, page_not_found
from models.workloads import find_workload_by_id
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


def workloads(request: HttpRequest) -> HttpResponse:
    """Отобразить общий список учебных поручений."""
    _, _, workloads_list = _load_data()

    rows = []
    for w in workloads_list:
        status_badge = (
            '<span class="badge bg-secondary">Отменено</span>'
            if w.is_cancelled
            else '<span class="badge bg-success">Активно</span>'
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
            <a href="/workloads/{w.id}/"
               class="text-decoration-none">
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
            <a href="/workloads/{w.id}/"
               class="btn btn-sm btn-outline-primary">
              Карточка
            </a>
          </td>
        </tr>
        """)

    table_rows = "".join(rows) if rows else """
    <tr><td colspan="11" class="text-center py-4">Список пуст</td></tr>
    """

    content = f"""
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h2 class="h3 fw-bold mb-0">Учебные поручения</h2>
      <span class="badge bg-primary fs-6">
        Всего: {len(workloads_list)}
      </span>
    </div>

    <div class="card shadow-sm border-0">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="table-dark">
            <tr>
              <th class="text-center" style="width: 50px;">ID</th>
              <th>Преподаватель</th>
              <th>Дисциплина</th>
              <th class="text-center">Сем.</th>
              <th class="text-center">Лек.</th>
              <th class="text-center">Прак.</th>
              <th class="text-center">Лаб.</th>
              <th class="text-center">Экз.</th>
              <th class="text-end">Итого</th>
              <th class="text-center">Статус</th>
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
    return HttpResponse(page("Список учебных поручений", content))


def workload_detail(request: HttpRequest, workload_id: int) -> HttpResponse:
    """Отобразить детальную информацию об учебном поручении."""
    _, _, workloads_list = _load_data()
    workload = find_workload_by_id(workloads_list, workload_id)
    if not workload:
        return page_not_found(request)

    status_badge = (
        '<span class="badge bg-secondary fs-6">Отменено</span>'
        if workload.is_cancelled
        else '<span class="badge bg-success fs-6">Активно</span>'
    )

    content = f"""
    <div class="mb-3">
      <a href="/workloads/" class="btn btn-outline-secondary btn-sm">
        &larr; Назад к списку поручений
      </a>
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
            <div class="p-3 bg-light rounded">
              <div class="fs-5 fw-bold">
                <a href="/teachers/{workload.teacher.id}/"
                   class="text-decoration-none">
                  {workload.teacher.name}
                </a>
              </div>
              <div class="text-muted small">
                {workload.teacher.position} &bull;
                Кафедра: {workload.teacher.department}
              </div>
              <div class="mt-2">
                <span class="badge bg-secondary">
                  Ставка: {workload.teacher.rate:.2f}
                </span>
              </div>
            </div>
          </div>

          <div class="col-md-6">
            <h5 class="fw-bold text-secondary">Объем часов по видам</h5>
            <ul class="list-group list-group-flush">
              <li class="list-group-item d-flex justify-content-between">
                <span>Лекции:</span>
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
                <span>Прием экзаменов:</span>
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

        <div class="mt-4 pt-3 border-top d-flex gap-2">
          <a href="/teachers/{workload.teacher.id}/"
             class="btn btn-outline-primary">
            Карточка преподавателя &rarr;
          </a>
          <a href="/workloads/" class="btn btn-outline-secondary">
            Все поручения
          </a>
        </div>
      </div>
    </div>
    """
    return HttpResponse(
        page(f"Учебное поручение #{workload.id}", content)
    )
