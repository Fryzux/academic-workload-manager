# Система учета учебной нагрузки преподавателей (Academic Workload Manager)

Веб-приложение на базе **Django 5.2** с использованием **Django Template Language (DTL)** и консольное объектно-ориентированное приложение для автоматизации процессов планирования, учета, анализа и контроля учебной нагрузки преподавателей кафедры высшего учебного заведения.

Разработано в рамках практических работ №1–№6 по дисциплине «Технологии разработки приложений на базе фреймворков» (РТУ МИРЭА).
Тема проекта № 488: «Система учета учебной нагрузки преподавателей».

## 1. Назначение проекта
Проект предназначен для автоматизации учебно-организационной работы кафедры: распределения учебных дисциплин между преподавателями, детализации часов (лекции, практики, лабы, экзамены), проверки соблюдения годовых норм по трудовым договорам (базовая норма 900 ч на полную ставку, допустимый интервал &plusmn;5%) и предоставления удобного веб-интерфейса.

## 2. Используемые технологии
- Python 3.10+ (протестировано на Python 3.14);
- Django 5.2 (LTS);
- Django Template Language (DTL): базовые и включаемые шаблоны, блоки, фильтры;
- HTML5, CSS3, JavaScript;
- Bootstrap 5.3 CDN + собственный CSS проекта;
- JSON для постоянного хранения данных;
- Git;
- pytest;
- flake8 (PEP 8, лимит строки 79 символов).

## 3. Архитектура веб-интерфейса и шаблонов (ПР6)
В ПР6 веб-часть проекта полностью переведена с генерации HTML-строк в Python-функциях (`page()`) на стандартную шаблонную архитектуру Django:
`View -> Context -> Template -> HTML`.

### Базовый шаблон и компоненты:
- **`templates/base.html`** — единый каркас сайта: метатеги, подключение Bootstrap 5.3, собственного CSS, шапки с логотипом, подвала с динамическим годом через JavaScript и блоков `{% block title %}` и `{% block content %}`;
- **`templates/includes/navigation.html`** — подключаемый шаблон навигационной панели со ссылками на пространства имён через теги `{% url %}`;
- **`templates/404.html`** — пользовательская страница ошибки 404 Not Found;
- **Включаемые шаблоны приложений:**
  - `teachers/includes/teacher_card.html` — карточка преподавателя;
  - `workloads/includes/workload_status.html` — бейдж статуса поручения.

### Статические файлы:
- `homepage/static/homepage/css/style.css` — фирменные стили карточек, логотипа, бейджей и эффектов при наведении;
- `homepage/static/homepage/js/main.js` — клиентский JavaScript (динамическая установка года `#current-year`);
- `homepage/static/homepage/img/logo.png` — эмблема системы учета нагрузки.

### Именованные маршруты и пространства имён (Namespaces):
- `homepage:index` — главная страница;
- `teachers:list`, `teachers:detail`, `teachers:add` — преподаватели;
- `disciplines:list`, `disciplines:detail`, `disciplines:add` — дисциплины;
- `workloads:list`, `workloads:detail`, `workloads:toggle` — учебные поручения.

## 4. Структура проекта

```text
academic-workload-manager/
├── manage.py              # Консольная утилита управления Django
├── main.py                # Консольное ООП-приложение (ПР3)
├── storage.py             # Загрузка и сохранение объектов в JSON
├── utils.py               # Вспомогательные функции безопасного ввода
├── pytest.ini             # Конфигурация тестовой среды pytest
├── requirements.txt       # Зависимости проекта
│
├── workload_manager/      # Конфигурационный пакет проекта Django
│   ├── settings.py        # Настройки (TEMPLATES DIRS, STATIC, ru-RU, Europe/Moscow)
│   ├── urls.py            # Корневая маршрутизация, include() и handler404
│   ├── asgi.py            # Точка входа ASGI
│   └── wsgi.py            # Точка входа WSGI
│
├── templates/             # Шаблоны уровня проекта
│   ├── base.html          # Базовый каркас сайта
│   ├── 404.html           # Страница ошибки 404
│   └── includes/
│       └── navigation.html # Панель навигации
│
├── homepage/              # Приложение главной страницы
│   ├── static/homepage/   # Статические файлы (css/style.css, js/main.js, img/logo.png)
│   ├── templates/homepage/index.html # Главная страница (сводка кафедры)
│   ├── views.py           # Представления index() и page_not_found()
│   └── urls.py            # Маршрут homepage:index
│
├── teachers/              # Приложение учета преподавателей
│   ├── templates/teachers/
│   │   ├── teacher_list.html     # Список преподавателей (фильтр |length)
│   │   ├── teacher_detail.html   # Карточка преподавателя ({% if %}, прогресс-бар)
│   │   ├── teacher_form.html     # Форма добавления преподавателя
│   │   └── includes/teacher_card.html # Включаемый шаблон карточки
│   ├── views.py           # teachers(), teacher_detail(), teacher_add()
│   └── urls.py            # Маршруты teachers:list, detail, add
│
├── disciplines/           # Приложение каталога дисциплин
│   ├── templates/disciplines/
│   │   ├── disciplines_list.html # Каталог предметов
│   │   ├── discipline_detail.html # Карточка предмета
│   │   └── discipline_form.html  # Форма добавления предмета
│   ├── views.py           # disciplines_list(), discipline_detail(), discipline_add()
│   └── urls.py            # Маршруты disciplines:list, detail, add
│
├── workloads/             # Приложение учебных поручений
│   ├── templates/workloads/
│   │   ├── workload_list.html    # Реестр поручений (фильтры, поиск)
│   │   ├── workload_detail.html  # Детальная карточка часов
│   │   └── includes/workload_status.html # Включаемый бейдж статуса
│   ├── views.py           # workloads(), workload_detail(), workload_toggle()
│   └── urls.py            # Маршруты workloads:list, detail, toggle
│
├── models/                # Доменные ООП-классы предметной области
│   ├── teachers.py        # Класс Teacher и бизнес-логика
│   ├── disciplines.py     # Класс Discipline
│   └── workloads.py       # Класс Workload и расчет соответствия норме
│
├── data/                  # Персистентное хранилище JSON
│   ├── teachers.json      # База преподавателей
│   ├── disciplines.json   # База дисциплин
│   └── workloads.json     # Журнал поручений
│
└── tests/                 # Модульные автоматические тесты
    ├── test_teachers.py    # Тесты класса Teacher
    ├── test_disciplines.py # Тесты класса Discipline
    ├── test_workloads.py   # Тесты расчетов нагрузки
    └── test_views.py       # Тесты представлений, маршрутов, DTL и статики
```

## 5. Хранение данных и дальнейшее развитие
На этапе ПР6 данные продолжают храниться в JSON-файлах каталога `data/` с восстановлением связей через модуль `storage.py`. Django ORM и реляционная СУБД пока не используются (запланированы на ПР7).

## 6. Запуск и проверка проекта

### Запуск веб-сервера разработки:
```powershell
python manage.py runserver
```
Веб-интерфейс доступен в браузере: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### Запуск консольной версии (ПР3):
```powershell
python main.py
```

### Запуск автоматических тестов:
```powershell
pytest -v
```

### Проверка стиля кода (PEP 8):
```powershell
flake8 --max-line-length=79 --exclude=.venv,*/migrations/*
```
