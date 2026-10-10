"""
Представления для приложения homepage.
"""

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from models.workloads import get_teacher_total_hours
from storage import load_disciplines, load_teachers, load_workloads

BOOTSTRAP_CSS = (
    "https://cdn.jsdelivr.net/npm/"
    "bootstrap@5.3.3/dist/css/bootstrap.min.css"
)


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


def page(title: str, content: str) -> str:
    """Сформировать базовую HTML-страницу с Bootstrap 5."""
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — Учет нагрузки</title>
  <link rel="stylesheet" href="{BOOTSTRAP_CSS}">
</head>
<body class="bg-light d-flex flex-column min-vh-100">
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4 shadow-sm">
    <div class="container">
      <a class="navbar-brand fw-bold" href="/">Учебная нагрузка</a>
      <div class="navbar-nav">
        <a class="nav-link" href="/">Главная</a>
        <a class="nav-link" href="/teachers/">Преподаватели</a>
        <a class="nav-link" href="/workloads/">Поручения</a>
      </div>
    </div>
  </nav>
  <main class="container mb-5 flex-grow-1">
    {content}
  </main>
  <footer class="bg-white border-top py-3 text-center text-muted small">
    <div class="container">
      РТУ МИРЭА &bull; ЭФБО-12-24 &bull; Учет учебной нагрузки (ПР5)
    </div>
  </footer>
</body>
</html>"""


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница со сводной аналитической панелью кафедры."""
    st = _load_stats()
    content = f"""
    <div class="p-5 mb-4 bg-white rounded-3 shadow-sm border">
      <div class="container-fluid py-2">
        <h1 class="display-6 fw-bold text-primary">
          Система учета учебной нагрузки преподавателей
        </h1>
        <p class="col-md-10 fs-5 text-secondary mt-3">
          Веб-приложение кафедры для контроля распределения
          академических часов, анализа выполнения индивидуальных норм
          и проверки соответствия занимаемым ставкам.
        </p>
        <div class="d-flex gap-2 mt-4">
          <a href="/teachers/" class="btn btn-primary btn-lg px-4">
            Преподаватели
          </a>
          <a href="/workloads/" class="btn btn-outline-secondary btn-lg px-4">
            Учебные поручения
          </a>
        </div>
      </div>
    </div>

    <div class="row g-3 mb-4">
      <div class="col-md-3 col-6">
        <div class="card border-0 shadow-sm p-3 text-center bg-white">
          <div class="text-muted small">Преподавателей</div>
          <div class="fs-3 fw-bold text-dark">{st['teachers_count']} чел.</div>
          <div class="small text-muted">
            Ставка суммарно: {st['total_rate']:.2f}
          </div>
        </div>
      </div>
      <div class="col-md-3 col-6">
        <div class="card border-0 shadow-sm p-3 text-center bg-white">
          <div class="text-muted small">Учебных поручений</div>
          <div class="fs-3 fw-bold text-primary">
            {st['active_workloads_count']} / {st['workloads_count']}
          </div>
          <div class="small text-muted">активных к общему числу</div>
        </div>
      </div>
      <div class="col-md-3 col-6">
        <div class="card border-0 shadow-sm p-3 text-center bg-white">
          <div class="text-muted small">Общий объем часов</div>
          <div class="fs-3 fw-bold text-success">
            {st['total_hours']:.1f} ч
          </div>
          <div class="small text-muted">активной нагрузки кафедры</div>
        </div>
      </div>
      <div class="col-md-3 col-6">
        <div class="card border-0 shadow-sm p-3 text-center bg-white">
          <div class="text-muted small">Соблюдение норм</div>
          <div class="fs-3 fw-bold text-info">
            {st['norm_count']} из {st['teachers_count']}
          </div>
          <div class="small text-muted">
            в норме (допуск &plusmn;5%)
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4 mb-4">
      <div class="col-md-6">
        <div class="card h-100 shadow-sm border-0">
          <div class="card-header bg-dark text-white fw-bold">
            Распределение академических часов по видам
          </div>
          <div class="card-body">
            <ul class="list-group list-group-flush">
              <li class="list-group-item d-flex justify-content-between">
                <span>Лекционные занятия:</span>
                <span class="fw-bold">{st['total_lectures']:.1f} ч</span>
              </li>
              <li class="list-group-item d-flex justify-content-between">
                <span>Практические занятия:</span>
                <span class="fw-bold">{st['total_practices']:.1f} ч</span>
              </li>
              <li class="list-group-item d-flex justify-content-between">
                <span>Лабораторные работы:</span>
                <span class="fw-bold">{st['total_labs']:.1f} ч</span>
              </li>
              <li class="list-group-item d-flex justify-content-between">
                <span>Прием экзаменов:</span>
                <span class="fw-bold">{st['total_exams']:.1f} ч</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card h-100 shadow-sm border-0">
          <div class="card-header bg-dark text-white fw-bold">
            Состояние индивидуальной нагрузки
          </div>
          <div class="card-body d-flex flex-column justify-content-center">
            <div class="mb-3 d-flex justify-content-between">
              <span>Соответствуют годовой норме:</span>
              <span class="badge bg-success fs-6">{st['norm_count']}</span>
            </div>
            <div class="mb-3 d-flex justify-content-between">
              <span>Преподаватели с недогрузкой:</span>
              <span class="badge bg-warning text-dark fs-6">
                {st['under_count']}
              </span>
            </div>
            <div class="mb-3 d-flex justify-content-between">
              <span>Преподаватели с перегрузкой:</span>
              <span class="badge bg-danger fs-6">{st['over_count']}</span>
            </div>
            <div class="mt-2 text-muted small">
              Базовая норма: 900 часов на полную ставку (1.0). Допустимое
              отклонение согласно Положению об учебной нагрузке: &plusmn;5%.
            </div>
          </div>
        </div>
      </div>
    </div>
    """
    return HttpResponse(page("Главная страница", content))


def page_not_found(request: HttpRequest, exception=None) -> HttpResponse:
    """Пользовательская страница ошибки 404 (Не найдено)."""
    content = """
    <div class="card border-danger shadow-sm my-4">
      <div class="card-header bg-danger text-white fw-bold">
        Ошибка 404 &bull; Страница не найдена
      </div>
      <div class="card-body py-4">
        <h4 class="card-title text-danger">Запрошенный ресурс не найден</h4>
        <p class="card-text text-muted">
          К сожалению, запрашиваемый адрес отсутствует или объект с
          указанным идентификатором был удален.
        </p>
        <div class="mt-4">
          <a href="/" class="btn btn-primary me-2">На главную</a>
          <a href="/teachers/" class="btn btn-outline-secondary me-2">
            Преподаватели
          </a>
          <a href="/workloads/" class="btn btn-outline-secondary">
            Поручения
          </a>
        </div>
      </div>
    </div>
    """
    return HttpResponse(
        page("Ошибка 404: Страница не найдена", content),
        status=404,
    )
