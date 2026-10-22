"""
Скрипт генерации академического отчета по ПР7 в формате DOCX.
"""

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Установить внутренние отступы ячейки таблицы."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in (
        ("top", top),
        ("bottom", bottom),
        ("left", left),
        ("right", right),
    ):
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def create_report():
    """Сформировать файл Отчет_ПР7.docx."""
    doc = Document()

    # Поля страницы: 2 см
    section = doc.sections[0]
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(1.5)

    # Базовый стиль Normal
    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Times New Roman"
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(4)

    # 1. Заголовок отчета
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    run_title = p_title.add_run("ОТЧЕТ ПО ПРАКТИЧЕСКОЙ РАБОТЕ № 7")
    run_title.font.name = "Times New Roman"
    run_title.font.size = Pt(14)
    run_title.bold = True

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(14)
    run_sub = p_sub.add_run(
        "«Основы баз данных и SQL»"
    )
    run_sub.font.name = "Times New Roman"
    run_sub.font.size = Pt(12)
    run_sub.bold = True

    def add_section_header(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(13)
        run.bold = True
        return p

    def add_bullet(bold_prefix, text):
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        r_bold = p.add_run(bold_prefix)
        r_bold.font.name = "Times New Roman"
        r_bold.bold = True
        r_text = p.add_run(text)
        r_text.font.name = "Times New Roman"
        return p

    # Раздел 1
    add_section_header("1. Общие сведения")
    add_bullet(
        "Дисциплина: ",
        "Технологии разработки приложений на базе фреймворков",
    )
    add_bullet(
        "Институт / Кафедра: ",
        "Институт перспективных технологий и индустриального "
        "программирования / Индустриального программирования",
    )
    add_bullet("Преподаватель: ", "Ящун Татьяна Викторовна")
    add_bullet(
        "Номер и тема работы: ",
        "Практическая работа № 7. «Основы баз данных и SQL». "
        "Тема № 488: «Система учета учебной нагрузки преподавателей»",
    )
    add_bullet("Группа: ", "ЭФБО-12-24")
    add_bullet("ФИО студента: ", "Лэ Дык Тхань Дат")
    add_bullet("Вариант: ", "488")
    add_bullet("Семестр: ", "5 семестр, 2026-2027")
    add_bullet("Год выполнения: ", "2026")

    # Раздел 2
    add_section_header("2. Цель работы")
    p_goal = doc.add_paragraph()
    p_goal.paragraph_format.space_after = Pt(4)
    p_goal.paragraph_format.line_spacing = 1.15
    p_goal.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_goal = p_goal.add_run(
        "Изучить основные понятия реляционных баз данных и языка SQL, освоить "
        "работу с СУБД SQLite: проектирование структуры таблиц, определение "
        "первичных и внешних ключей, создание таблиц средствами DDL "
        "(sql/schema.sql); перенос существующих данных проекта из JSON в "
        "таблицы SQLite (db/import_json.py); разработка прикладных "
        "SQL-запросов (SELECT, WHERE, JOIN, COUNT, SUM, AVG, GROUP BY, "
        "HAVING, подзапрос NOT IN); получение результатов SQL-запросов в "
        "представлениях Django средствами sqlite3 (sqlite3.Row) и их "
        "отображение на страницах сайта."
    )
    r_goal.font.name = "Times New Roman"

    # Раздел 3
    add_section_header("3. Выполненные материалы Яндекс Практикума")

    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    hdr_cells = table.rows[0].cells
    hdr_cells[0].width = Cm(5.5)
    hdr_cells[1].width = Cm(11.5)

    hdr_cells[0].paragraphs[0].paragraph_format.space_after = Pt(2)
    r0 = hdr_cells[0].paragraphs[0].add_run("Раздел")
    r0.font.name = "Times New Roman"
    r0.bold = True

    hdr_cells[1].paragraphs[0].paragraph_format.space_after = Pt(2)
    r1 = hdr_cells[1].paragraphs[0].add_run("Выполненные темы")
    r1.font.name = "Times New Roman"
    r1.bold = True

    topics = [
        (
            "Раздел 05.\n«Базы данных и Django ORM»",
            "Введение в спринт; Базы данных: реляционные и не только; "
            "SQL: язык структурированных запросов; Первые запросы, первые "
            "результаты; Работа с базой данных из Python; Получение данных; "
            "Практика запросов; Сортировка, ограничение и сдвиг выборки; "
            "Агрегирующие функции; Группировка записей в выборке.",
        ),
    ]

    for section_title, content_desc in topics:
        row_cells = table.add_row().cells
        row_cells[0].width = Cm(5.5)
        row_cells[1].width = Cm(11.5)

        p_sec = row_cells[0].paragraphs[0]
        p_sec.paragraph_format.space_after = Pt(2)
        r_sec = p_sec.add_run(section_title)
        r_sec.font.name = "Times New Roman"
        r_sec.bold = True

        p_desc = row_cells[1].paragraphs[0]
        p_desc.paragraph_format.space_after = Pt(2)
        r_desc = p_desc.add_run(content_desc)
        r_desc.font.name = "Times New Roman"

        set_cell_margins(row_cells[0])
        set_cell_margins(row_cells[1])

    # Раздел 4
    add_section_header("4. Доработка индивидуального проекта")
    add_bullet(
        "Название проекта: ",
        "«Система учета учебной нагрузки преподавателей» "
        "(Academic Workload Manager).",
    )
    add_bullet(
        "Схема реляционной базы данных (data/workload.sqlite):\n",
        "1) teachers (id PK, name, position, department, rate);\n"
        "2) disciplines (id PK, name, department, semester);\n"
        "3) workloads (id PK, teacher_id FK, discipline_id FK, lectures, "
        "practices, labs, exams, total_hours, is_cancelled);\n"
        "4) Включение проверки внешних ключей: PRAGMA foreign_keys = ON.",
    )
    add_bullet(
        "Организация модулей подсистемы SQLite:\n",
        "• sql/schema.sql — команды создания таблиц и внешних ключей;\n"
        "• sql/queries.sql — комплекс из 12 прикладных SQL-запросов;\n"
        "• db/database.py — подключение с row_factory = sqlite3.Row;\n"
        "• db/import_json.py — перенос существующих данных из JSON в SQLite.",
    )
    add_bullet(
        "Интеграция с Django и сценарии предметной области:\n",
        "• disciplines:available (/disciplines/available/) — поиск "
        "свободных дисциплин кафедры (подзапрос NOT IN);\n"
        "• workloads:statistics (/workloads/statistics/) — агрегаты "
        "(COUNT, SUM, AVG) и группировка (GROUP BY / HAVING);\n"
        "• Синхронизация добавления преподавателей, предметов и изменения "
        "активности поручений с базой SQLite.",
    )
    add_bullet(
        "Сохранение существующей кодовой базы:\n",
        "• Доменные классы ООП, функции JSON-хранилища и интерактивная "
        "консольная версия main.py полностью сохранены и работоспособны;\n"
        "• ORM Django не внедрялся преждевременно (согласно методике ПР7).",
    )
    add_bullet(
        "Ссылка на Git-репозиторий: ",
        "https://github.com/Fryzux/academic-workload-manager",
    )

    # Раздел 5
    add_section_header("5. Результат работы")
    p_res_lead = doc.add_paragraph()
    p_res_lead.paragraph_format.space_after = Pt(2)
    r_lead = p_res_lead.add_run(
        "В результате выполнения практической работы № 7:"
    )
    r_lead.font.name = "Times New Roman"

    add_bullet(
        "Спроектирована и развернута база данных SQLite: ",
        "созданы таблицы teachers, disciplines, workloads со связями FK;",
    )
    add_bullet(
        "Выполнен перенос данных: ",
        "скрипт db/import_json.py перенес записи из JSON в SQLite с "
        "обеспечением целостности;",
    )
    add_bullet(
        "Сформирован каталог проверенных запросов: ",
        "файл sql/queries.sql содержит 12 запросов (WHERE, JOIN, COUNT, "
        "SUM, AVG, GROUP BY, HAVING, NOT IN);",
    )
    add_bullet(
        "Реализованы рабочие сценарии Django: ",
        "страницы каталогов, поиск нераспределенных дисциплин и страница "
        "сводной статистики кафедры;",
    )
    add_bullet(
        "Безопасность SQL: ",
        "все значения параметров передаются через плейсхолдеры ?.",
    )

    # Раздел 6
    add_section_header("6. Проверка работоспособности")
    add_bullet(
        "python manage.py check: ",
        "System check identified no issues (0 silenced).",
    )
    add_bullet(
        "pytest -v: ",
        "42 passed (100% тестов успешно пройдены за 0.49 с).",
    )
    add_bullet(
        "flake8 --max-line-length=79: ",
        "0 ошибок, 0 предупреждений (полное соблюдение стандарта PEP 8).",
    )

    # Раздел 7
    add_section_header("7. Чек-лист индивидуального проекта (по п. 7.2)")

    t_check = doc.add_table(rows=1, cols=3)
    t_check.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_check.autofit = False

    ch_hdr = t_check.rows[0].cells
    ch_hdr[0].width = Cm(1.2)
    ch_hdr[1].width = Cm(13.8)
    ch_hdr[2].width = Cm(2.0)

    for i, title in enumerate(["№", "Требование", "Статус"]):
        p = ch_hdr[i].paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(title)
        r.font.name = "Times New Roman"
        r.bold = True
        set_cell_margins(ch_hdr[i])

    checklist_items = [
        "Проект ПР1–ПР6 сохранён и продолжен",
        "Определены сущности предметной области",
        "Определены таблицы (teachers, disciplines, workloads)",
        "Определены поля и типы данных",
        "Определены первичные ключи (PRIMARY KEY)",
        "Определены необходимые внешние ключи (FOREIGN KEY)",
        "Создан файл базы данных SQLite (data/workload.sqlite)",
        "Таблицы созданы средствами SQL (sql/schema.sql)",
        "Создан модуль подключения db/database.py",
        "Включена проверка внешних ключей (PRAGMA foreign_keys = ON)",
        "Создан скрипт переноса данных db/import_json.py",
        "Данные перенесены из JSON-файлов",
        "Импортированные данные проверены",
        "Создан файл sql/queries.sql",
        "Запросы проверены в SQLite CLI",
        "Использованы SELECT и WHERE",
        "Использован JOIN для связанных данных",
        "Использованы агрегатные функции (COUNT, SUM, AVG)",
        "Выполнена группировка (GROUP BY)",
        "Выполнена фильтрация групп (HAVING)",
        "Значения передаются параметрами ?",
        "Использован sqlite3.Row в представлениях",
        "Список преподавателей выводится из SQLite",
        "Список поручений выводится со связями через JOIN",
        "Реализован поиск свободных дисциплин по семестру (NOT IN)",
        "Реализована страница статистики",
        "Настроена навигация между разделами",
        "Обновлён README.md",
        "Выполнены проверки проекта (check, pytest, flake8)",
        "Изменения сохранены в Git с меткой PR7:",
        "Разработано не менее 10 SQL-запросов разного вида",
    ]

    for idx, item_text in enumerate(checklist_items, 1):
        row_cells = t_check.add_row().cells
        row_cells[0].width = Cm(1.2)
        row_cells[1].width = Cm(13.8)
        row_cells[2].width = Cm(2.0)

        p0 = row_cells[0].paragraphs[0]
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(str(idx))
        r0.font.name = "Times New Roman"

        p1 = row_cells[1].paragraphs[0]
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(item_text)
        r1.font.name = "Times New Roman"

        p2 = row_cells[2].paragraphs[0]
        p2.paragraph_format.space_after = Pt(2)
        r2 = p2.add_run("Выполнено")
        r2.font.name = "Times New Roman"
        r2.bold = True

        set_cell_margins(row_cells[0])
        set_cell_margins(row_cells[1])
        set_cell_margins(row_cells[2])

    # Раздел 8
    add_section_header("8. Вывод")
    p_concl = doc.add_paragraph()
    p_concl.paragraph_format.space_before = Pt(2)
    p_concl.paragraph_format.space_after = Pt(6)
    p_concl.paragraph_format.line_spacing = 1.15
    p_concl.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_concl = p_concl.add_run(
        "В ходе выполнения практической работы № 7 были практически освоены "
        "фундаментальные основы реляционных баз данных и языка SQL "
        "применительно к СУБД SQLite. Проект «Система учета учебной нагрузки "
        "преподавателей» переведен от чисто файловой обработки данных к "
        "реляционной архитектуре. Использование SQL-соединений JOIN, "
        "агрегатных функций COUNT, SUM, AVG и группировок GROUP BY / HAVING "
        "позволило реализовать выборку и расчет аналитических показателей "
        "кафедры непосредственно на уровне СУБД. Высокое качество и "
        "надежность кода подтверждены 42 тестами pytest и проверкой PEP 8."
    )
    r_concl.font.name = "Times New Roman"

    out_path = r"C:\Users\nolik\Desktop\Отчет_ПР7.docx"
    doc.save(out_path)
    print(f"Отчет успешно сохранен: {out_path}")


if __name__ == "__main__":
    create_report()
