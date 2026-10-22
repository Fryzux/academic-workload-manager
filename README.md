# Система учета учебной нагрузки преподавателей (Academic Workload Manager)

Веб-приложение на базе **Django 5.2**, реляционной базы данных **SQLite**, шаблонизатора **Django Template Language (DTL)** и консольное объектно-ориентированное приложение для комплексной автоматизации процессов планирования, учета, анализа и контроля учебной нагрузки преподавателей кафедры высшего учебного заведения.

Разработано в рамках практических работ №1–№7 по дисциплине «Технологии разработки приложений на базе фреймворков» (РТУ МИРЭА).  
Тема проекта № 488: «Система учета учебной нагрузки преподавателей».

---

## 1. Назначение проекта
Проект предназначен для автоматизации учебно-организационной работы кафедры: распределения учебных дисциплин между преподавателями, детализации часов (лекции, практики, лабы, экзамены), проверки соблюдения годовых норм по трудовым договорам (базовая норма 900 ч на полную ставку, допустимый интервал &plusmn;5%), выполнения аналитических SQL-запросов и предоставления удобного веб-интерфейса.

---

## 2. Используемые технологии
- **Python 3.10+** (протестировано на Python 3.14);
- **Django 5.2** (LTS);
- **SQLite 3** и стандартная библиотека `sqlite3` (`row_factory = sqlite3.Row`);
- **SQL** (DDL, SELECT, WHERE, JOIN, GROUP BY, HAVING, подзапросы NOT IN, агрегатные функции);
- **Django Template Language (DTL)**: базовые и включаемые шаблоны, блоки, фильтры;
- **HTML5, CSS3, JavaScript**;
- **Bootstrap 5.3 CDN** + собственный CSS проекта;
- **JSON** для исторической обратной совместимости;
- **Git**;
- **pytest** (42 теста);
- **flake8** (PEP 8, ограничение строки 79 символов).

---

## 3. Слой реляционной базы данных SQLite и SQL (ПР7)
В рамках ПР7 индивидуальный проект получил полноценный слой реляционного хранения и обработки данных средствами СУБД SQLite без преждевременного внедрения Django ORM:

### 3.1. Структура базы данных (`data/workload.sqlite`)
1. **Таблица `teachers`:**
   - `id` (INTEGER PRIMARY KEY) — уникальный идентификатор преподавателя;
   - `name` (TEXT NOT NULL) — ФИО преподавателя;
   - `position` (TEXT NOT NULL) — должность;
   - `department` (TEXT NOT NULL) — кафедра;
   - `rate` (REAL NOT NULL) — занимаемая доля ставки.
2. **Таблица `disciplines`:**
   - `id` (INTEGER PRIMARY KEY) — идентификатор дисциплины;
   - `name` (TEXT NOT NULL) — наименование предмета;
   - `department` (TEXT NOT NULL) — закрепляющая кафедра;
   - `semester` (INTEGER NOT NULL) — семестр преподавания.
3. **Таблица `workloads`:**
   - `id` (INTEGER PRIMARY KEY) — идентификатор поручения;
   - `teacher_id` (INTEGER NOT NULL) — внешний ключ (`REFERENCES teachers(id)`);
   - `discipline_id` (INTEGER NOT NULL) — внешний ключ (`REFERENCES disciplines(id)`);
   - `lectures` (REAL NOT NULL) — лекционные часы;
   - `practices` (REAL NOT NULL) — практические занятия;
   - `labs` (REAL NOT NULL) — лабораторные работы;
   - `exams` (REAL NOT NULL) — прием зачетов/экзаменов;
   - `total_hours` (REAL NOT NULL) — итоговая нагрузка;
   - `is_cancelled` (INTEGER NOT NULL DEFAULT 0) — признак отмены поручения.

### 3.2. Файлы подсистемы баз данных
- **`sql/schema.sql`** — DDL-скрипт создания схемы данных с ограничениями `PRIMARY KEY`, `FOREIGN KEY` и включением `PRAGMA foreign_keys = ON;`;
- **`sql/queries.sql`** — проверенный набор из 12 прикладных SQL-запросов (выборки, фильтрация WHERE, соединение JOIN, подзапрос NOT IN, агрегации COUNT/SUM/AVG, группировка GROUP BY и фильтрация групп HAVING);
- **`db/database.py`** — модуль подключения с настройкой `row_factory = sqlite3.Row` и автоматической проверкой целостности связей;
- **`db/import_json.py`** — скрипт однократного и периодического переноса данных из JSON в SQLite с соблюдением порядка связей.

### 3.3. Веб-сценарии с использованием SQL в Django
- **Просмотр каталогов из SQLite:** списки преподавателей и предметов формируются с помощью прямых запросов к базе;
- **Поиск нераспределенных (свободных) дисциплин (`/disciplines/available/`):** параметризованный SQL-запрос с подзапросом `NOT IN` и фильтрацией по семестру;
- **Сводная статистика кафедры (`/workloads/statistics/`):** агрегированные показатели (COUNT, SUM, AVG), распределение часов по преподавателям (LEFT JOIN + GROUP BY) и по семестрам (JOIN + GROUP BY).

---

## 4. Структура проекта

```text
academic-workload-manager/
├── manage.py              # Консольная утилита управления Django
├── main.py                # Консольное ООП-приложение (ПР3)
├── storage.py             # Загрузка и сохранение объектов в JSON
├── utils.py               # Вспомогательные функции ввода
├── pytest.ini             # Конфигурация тестовой среды pytest
├── requirements.txt       # Зависимости проекта
│
├── sql/                   # Скрипты реляционной базы данных (ПР7)
│   ├── schema.sql         # Схема создания таблиц и внешних ключей
│   └── queries.sql        # Набор проверенных SQL-запросов
│
├── db/                    # Пакет прямого подключения к SQLite (ПР7)
│   ├── __init__.py        # Маркер пакета Python
│   ├── database.py        # get_connection(), PRAGMA foreign_keys, Row
│   └── import_json.py     # Перенос существующих данных из JSON в SQLite
│
├── data/                  # Хранилище данных
│   ├── workload.sqlite    # Реляционная база данных SQLite (ПР7)
│   ├── teachers.json      # Исходные данные преподавателей
│   ├── disciplines.json   # Исходные данные дисциплин
│   └── workloads.json     # Исходные данные поручений
│
├── workload_manager/      # Конфигурационный пакет проекта Django
│   ├── settings.py        # Настройки (TEMPLATES, STATIC, ru-RU)
│   ├── urls.py            # Корневая маршрутизация и handler404
│   ├── asgi.py            # Точка входа ASGI
│   └── wsgi.py            # Точка входа WSGI
│
├── templates/             # Шаблоны уровня проекта (ПР6)
│   ├── base.html          # Базовый каркас сайта
│   ├── 404.html           # Страница ошибки 404
│   └── includes/
│       └── navigation.html # Панель навигации со ссылками
│
├── homepage/              # Приложение главной страницы
│   ├── static/homepage/   # Статические файлы (style.css, main.js, logo.png)
│   ├── templates/homepage/index.html # Главная страница (сводка кафедры)
│   ├── views.py           # Представления index() и page_not_found()
│   └── urls.py            # Маршрут homepage:index
│
├── teachers/              # Приложение учета преподавателей
│   ├── templates/teachers/
│   │   ├── teacher_list.html     # Список преподавателей
│   │   ├── teacher_detail.html   # Карточка преподавателя
│   │   ├── teacher_form.html     # Форма добавления преподавателя
│   │   └── includes/teacher_card.html # Включаемый шаблон карточки
│   ├── views.py           # teachers(), teacher_detail(), teacher_add()
│   └── urls.py            # Маршруты teachers:list, detail, add
│
├── disciplines/           # Приложение каталога дисциплин
│   ├── templates/disciplines/
│   │   ├── disciplines_list.html # Каталог предметов
│   │   ├── discipline_detail.html # Карточка предмета
│   │   ├── discipline_form.html  # Форма добавления предмета
│   │   └── available.html        # Поиск свободных дисциплин (SQL NOT IN)
│   ├── views.py           # disciplines_list(), available_disciplines()
│   └── urls.py            # Маршруты disciplines:list, available, add
│
├── workloads/             # Приложение учебных поручений
│   ├── templates/workloads/
│   │   ├── workload_list.html    # Реестр поручений (JOIN)
│   │   ├── workload_detail.html  # Детальная карточка часов
│   │   ├── statistics.html       # Статистика кафедры (GROUP BY / HAVING)
│   │   └── includes/workload_status.html # Включаемый бейдж статуса
│   ├── views.py           # workloads(), workload_detail(), statistics()
│   └── urls.py            # Маршруты workloads:list, detail, statistics
│
├── models/                # Доменные ООП-классы предметной области
│   ├── teachers.py        # Класс Teacher
│   ├── disciplines.py     # Класс Discipline
│   └── workloads.py       # Класс Workload
│
└── tests/                 # Модульные автоматические тесты
    ├── test_teachers.py    # Тесты класса Teacher
    ├── test_disciplines.py # Тесты класса Discipline
    ├── test_workloads.py   # Тесты расчетов нагрузки
    ├── test_views.py       # Тесты представлений, маршрутов и DTL
    └── test_sql_pr7.py     # Тесты SQLite, схемы, импорта и SQL-запросов
```

---

## 5. Запуск и проверка проекта

### Инициализация и импорт данных в SQLite:
```powershell
python -m db.import_json
```

### Запуск веб-сервера разработки Django:
```powershell
python manage.py runserver
```
Веб-интерфейс доступен в браузере: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### Основные страницы веб-приложения:
- Главная визитка: `/`
- Список преподавателей: `/teachers/`
- Карточка преподавателя: `/teachers/<id>/`
- Добавление преподавателя: `/teachers/add/`
- Каталог дисциплин: `/disciplines/`
- Поиск свободных дисциплин (SQL NOT IN): `/disciplines/available/`
- Каталог поручений: `/workloads/`
- Карточка поручения: `/workloads/<id>/`
- Сводная аналитика и статистика (SQL GROUP BY): `/workloads/statistics/`

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
