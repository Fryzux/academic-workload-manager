"""
Скрипт генерации академического отчета по ПР6 в формате DOCX.
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
    """Сформировать файл Отчет_ПР6.docx."""
    doc = Document()

    # Поля страницы: 2 см со всех сторон
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
    run_title = p_title.add_run("ОТЧЕТ ПО ПРАКТИЧЕСКОЙ РАБОТЕ № 6")
    run_title.font.name = "Times New Roman"
    run_title.font.size = Pt(14)
    run_title.bold = True

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(14)
    run_sub = p_sub.add_run(
        "«Шаблоны Django и проектная разработка»"
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
        "Практическая работа № 6. «Шаблоны Django и проектная разработка». "
        "Тема № 488: «Система учета учебной нагрузки преподавателей»",
    )
    add_bullet("Группа: ", "ЭФБО-12-24")
    add_bullet("ФИО студента: ", "Лэ Дык Тхань Дат")
    add_bullet("Вариант: ", "488")
    add_bullet("Год выполнения: ", "2026")

    # Раздел 2
    add_section_header("2. Цель работы")
    p_goal = doc.add_paragraph()
    p_goal.paragraph_format.space_after = Pt(4)
    p_goal.paragraph_format.line_spacing = 1.15
    p_goal.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_goal = p_goal.add_run(
        "Освоить шаблонизатор Django Template Language (DTL) и архитектурный "
        "шаблон MVT (Model-View-Template); перевести веб-интерфейс "
        "индивидуального сквозного проекта с генерации HTML-строк в Python "
        "на систему шаблонов Django; реализовать иерархию и наследование "
        "шаблонов (base.html), декомпозицию на включаемые фрагменты "
        "({% include %}), безопасную передачу контекста, именованные URL с "
        "пространствами имен (app_name), фильтры DTL и интеграцию статических "
        "файлов (CSS, JavaScript, медиа-ресурсы)."
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
            "Раздел 04.\n«Основы веб-разработки»\n"
            "Тема: «HTML и шаблоны Django»",
            "HTML в Django: шаблоны веб-страниц; HTML-шаблоны из частей: "
            "теги include, extends, block; Словарь контекста, ветвление и "
            "циклы в шаблонах; Ссылки в шаблонах: name и namespace; Фильтры "
            "в шаблонах: модифицируем контекст страницы; Подключение стилей, "
            "картинок и скриптов к шаблонам; Из тренажёра на компьютер; "
            "Правила оформления HTML и шаблонов Django; Создание шаблонов "
            "из HTML-документов.",
        ),
        (
            "Раздел 04.\n«Основы веб-разработки»\n"
            "Тема: «Финальный проект спринта Блогикум»",
            "Архитектура и структура приложения «Блогикум»; Наследование "
            "базового шаблона; Навигация и подключаемые блоки; Организация "
            "статических файлов и карточек записей; Обратная связь.",
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
        "Архитектура шаблонов DTL:\n",
        "1) В корне проекта сформирован каталог templates/, "
        "зарегистрированный в settings.py;\n"
        "2) Базовый каркас templates/base.html с блоками block title, "
        "block content, Bootstrap 5.3 CDN, CSS, логотипом и JS;\n"
        "3) Включаемые фрагменты templates/includes/navigation.html "
        "(меню со ссылками {% url %}), teacher_card.html и "
        "workload_status.html (бейдж статуса нормы);\n"
        "4) Полная ликвидация функции page() и прямой генерации HTML; "
        "перевод всех views на django.shortcuts.render();\n"
        "5) Организация пространств имён URL (app_name: 'homepage', "
        "'teachers', 'disciplines', 'workloads') и тег {% url %};\n"
        "6) Внедрение фильтров шаблонов (|length, |default, |floatformat) "
        "и обработчика 404.",
    )
    add_bullet(
        "Сохранение существующей кодовой базы:\n",
        "• Доменные классы ООП (Teacher, Discipline, Workload) сохранены;\n"
        "• Функции загрузки и сохранения в JSON (storage.py) сохранены;\n"
        "• Консольное интерактивное приложение main.py работоспособно;\n"
        "• ORM Django не внедрялся преждевременно (согласно плану).",
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
        "В результате выполнения практической работы № 6:"
    )
    r_lead.font.name = "Times New Roman"

    add_bullet(
        "Переход на DTL: ",
        "веб-интерфейс полностью освобожден от генерации HTML в строках "
        "Python, создано 10 DTL-шаблонов с наследованием;",
    )
    add_bullet(
        "Модульность и переиспользование: ",
        "шапка, навигация, карточки преподавателей и бейджи статуса выделены "
        "во включаемые шаблоны через тег {% include %};",
    )
    add_bullet(
        "Статические ресурсы: ",
        "в проекте организована структура homepage/static/homepage/ с "
        "файлами css/style.css, js/main.js и логотипом img/logo.png;",
    )
    add_bullet(
        "Надежная маршрутизация: ",
        "все ссылки в шаблонах и редиректы используют пространства имен и "
        "именованные маршруты (app_name:route_name);",
    )
    add_bullet(
        "Обработка ошибок: ",
        "реализован дружелюбный интерфейс страницы 404 (templates/404.html) с "
        "возвратом корректного кода состояния HTTP 404 Not Found.",
    )

    # Раздел 6
    add_section_header("6. Проверка работоспособности")
    add_bullet(
        "python manage.py check: ",
        "System check identified no issues (0 silenced).",
    )
    add_bullet(
        "pytest -v: ",
        "32 passed (100% тестов успешно пройдены за 0.61 с).",
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
        "Проект ПР1–ПР5 сохранён и продолжен",
        "Создана структура templates, настроен параметр DIRS",
        "Создан базовый шаблон base.html",
        "Используется {% extends %}",
        "Используются {% block %}",
        "Используется {% include %}",
        "Навигация вынесена в отдельный шаблон",
        "Созданы шаблоны для списка преподавателей (помещений)",
        "Создан шаблон отдельного преподавателя (помещения)",
        "Созданы шаблоны списка поручений (бронирований)",
        "Создан шаблон отдельного поручения (бронирования)",
        "Данные передаются через context",
        "Используется {% for %}",
        "Используется {% if %}",
        "Обрабатывается пустой список ({% empty %})",
        "Настроены app_name во всех приложениях",
        "Настроены именованные URL",
        "Используется тег {% url %}",
        "Используются пространства имён",
        "Используются фильтры шаблонов (|length, |default, |floatformat)",
        "Подключён собственный CSS (style.css)",
        "Подключено изображение (logo.png)",
        "Подключён JavaScript (main.js)",
        "page() больше не используется веб-представлениями",
        "Все основные страницы работают",
        "Данные предметной области отображаются из существующей модели",
        "JSON-хранилище ПР5 сохранено",
        "ORM не внедрялся преждевременно",
        "README.md обновлён",
        "python manage.py check выполнен без ошибок",
        "pytest -v выполнен успешно",
        "flake8 выполнен без замечаний",
        "Создан Git-коммит с префиксом PR6:",
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
        "В ходе выполнения практической работы № 6 были детально освоены "
        "механизмы шаблонизации Django Template Language, концепция "
        "наследования шаблонов, подключение статических файлов и "
        "организация архитектуры MVT. Индивидуальный сквозной проект "
        "«Система учета учебной нагрузки преподавателей» был переведен "
        "с низкоуровневой генерации HTML на декларативные DTL-шаблоны, "
        "что существенно повысило читаемость кода, расширяемость и "
        "безопасность веб-приложения. Качество кода валидировано 32 "
        "тестами и анализатором flake8."
    )
    r_concl.font.name = "Times New Roman"

    out_path = r"C:\Users\nolik\Desktop\Отчет_ПР6.docx"
    doc.save(out_path)
    print(f"Отчет успешно сохранен: {out_path}")


if __name__ == "__main__":
    create_report()
