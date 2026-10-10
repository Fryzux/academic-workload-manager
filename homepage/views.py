"""
Представления для приложения homepage.
"""

from django.http import HttpRequest, HttpResponse

BOOTSTRAP_CSS = (
    "https://cdn.jsdelivr.net/npm/"
    "bootstrap@5.3.3/dist/css/bootstrap.min.css"
)


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
    """Главная страница системы учета учебной нагрузки."""
    content = """
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

    <div class="row g-4">
      <div class="col-md-4">
        <div class="card h-100 shadow-sm border-0">
          <div class="card-body">
            <h5 class="card-title fw-bold">Преподаватели</h5>
            <p class="card-text text-muted">
              Учет профессорско-преподавательского состава кафедры,
              занимаемых ставок и закрепленных поручений.
            </p>
            <a href="/teachers/" class="btn btn-sm btn-outline-primary">
              Перейти к списку &rarr;
            </a>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100 shadow-sm border-0">
          <div class="card-body">
            <h5 class="card-title fw-bold">Учебные поручения</h5>
            <p class="card-text text-muted">
              Детализация часов: лекции, практические занятия,
              лабораторные работы и прием экзаменов.
            </p>
            <a href="/workloads/" class="btn btn-sm btn-outline-primary">
              Перейти к поручениям &rarr;
            </a>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100 shadow-sm border-0">
          <div class="card-body">
            <h5 class="card-title fw-bold">Консольный модуль</h5>
            <p class="card-text text-muted">
              Проект сохраняет полную совместимость с консольным
              приложением main.py и набором тестов pytest.
            </p>
            <span class="badge bg-success">Совместимо с ПР3</span>
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
