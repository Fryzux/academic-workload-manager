"""
Скрипт генерации академического отчета по ПР5 в формате DOCX.
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
    """Сформировать файл Отчет_ПР5.docx."""
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
    run_title = p_title.add_run("ОТЧЕТ ПО ПРАКТИЧЕСКОЙ РАБОТЕ № 5")
    run_title.font.name = "Times New Roman"
    run_title.font.size = Pt(14)
    run_title.bold = True

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(14)
    run_sub = p_sub.add_run(
        "«Django, HTTP и основы веб-разработки»"
    )
    run_sub.font.name = "Times New Roman"
    run_sub.font.size = Pt(12)
    run_sub.bold = True

    # Функция добавления заголовка раздела (БЕЗ ССЫЛОК)
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
        "Практическая работа № 5. «Django, HTTP и основы веб-разработки». "
        "Тема № 488: «Система учета учебной нагрузки преподавателей»",
    )
    add_bullet("Группа: ", "ЭФБО-12-24")
    add_bullet("ФИО студента: ", "Лэ Дык Тхань Дат")
    add_bullet("Год выполнения: ", "2026")

    # Раздел 2
    add_section_header("2. Выполненные материалы Яндекс Практикума")

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
            "Раздел 05.\n«Основы веб-разработки и протокол HTTP»",
            "Архитектура клиент-сервер; протокол HTTP (структура запроса "
            "и ответа, методы GET и POST, коды состояния 200 OK, 404 Not "
            "Found, 500 Internal Server Error); заголовки и тело HTTP-пакета.",
        ),
        (
            "Раздел 05.\n«Знакомство с веб-фреймворком Django»",
            "Архитектурный шаблон MVT; структура проекта Django (manage.py, "
            "settings.py, urls.py); создание и регистрация приложений (apps); "
            "маршрутизация запросов (urls.py, функция include, path "
            "converters <int:id>); функции-представления (views), классы "
            "HttpRequest и HttpResponse; обработка ошибок (кастомный "
            "handler404).",
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

    # Раздел 3
    add_section_header("3. Доработка индивидуального проекта")
    add_bullet(
        "Название проекта: ",
        "«Система учета учебной нагрузки преподавателей» "
        "(Academic Workload Manager).",
    )
    add_bullet(
        "Архитектура веб-приложения на базе Django 5.2:\n",
        "1) Конфигурационный модуль workload_manager (settings.py: "
        "русская локализация ru-RU, часовой пояс Europe/Moscow, регистрация "
        "приложений; urls.py: корневая диспетчеризация маршрутов и "
        "handler404 = 'homepage.views.page_not_found');\n"
        "2) Приложение homepage: главная страница (/), базовый шаблон "
        "страницы page() на Bootstrap 5.3 CDN, обработчик ошибки 404;\n"
        "3) Приложение teachers: реестр преподавателей (/teachers/) и "
        "детальная карточка нагрузки (/teachers/<int:teacher_id>/) со "
        "сводкой часов, ставкой, статусом соответствия и поручениями;\n"
        "4) Приложение workloads: сводный список поручений (/workloads/) "
        "и карточка поручения (/workloads/<int:workload_id>/) с детальным "
        "раскладом по видам работ (лекции, практики, лабы, экзамены).",
    )
    add_bullet(
        "Сохранение существующей кодовой базы (ООП и консоль):\n",
        "• Все доменные классы предметной области (Teacher, Discipline, "
        "Workload в пакете models/) сохранены в неизменном виде;\n"
        "• Функции загрузки и сохранения в JSON (storage.py) используются "
        "веб-представлениями для чтения данных и восстановления связей;\n"
        "• Интерактивное консольное приложение main.py полностью сохранено "
        "и работоспособно в терминале;\n"
        "• В модуль models/workloads.py добавлена функция "
        "find_workload_by_id для поиска поручения по ID.",
    )
    add_bullet(
        "Ссылка на Git-репозиторий: ",
        "https://github.com/Fryzux/academic-workload-manager",
    )

    # Раздел 4
    add_section_header("4. Результат работы")
    p_res_lead = doc.add_paragraph()
    p_res_lead.paragraph_format.space_after = Pt(2)
    r_lead = p_res_lead.add_run(
        "В результате выполнения практической работы № 5:"
    )
    r_lead.font.name = "Times New Roman"

    add_bullet(
        "Развернут веб-каркас Django 5.2: ",
        "создан проект workload_manager и 3 приложения (homepage, "
        "teachers, workloads), зарегистрированные в INSTALLED_APPS;",
    )
    add_bullet(
        "Реализована модульная маршрутизация: ",
        "настроены корневой и дочерние файлы urls.py с конвертерами "
        "путей <int:id>, подключенные через django.urls.include;",
    )
    add_bullet(
        "Разработаны функции-представления: ",
        "созданы views для главной страницы, списков и карточек сущностей, "
        "формирующие валидные ответы HttpResponse со статусами 200 и 404;",
    )
    add_bullet(
        "Интегрирован современный веб-интерфейс: ",
        "применен фреймворк Bootstrap 5.3 CDN, обеспечивающий адаптивную "
        "навигационную панель, таблицы, карточки и бейджи статуса нормы;",
    )
    add_bullet(
        "Настроена обработка ошибок: ",
        "внедрен пользовательский обработчик ошибки 404 Not Found "
        "с навигационными ссылками на рабочие разделы;",
    )
    add_bullet(
        "Расширено автоматизированное тестирование: ",
        "разработан модуль tests/test_views.py с 12 тестами на "
        "базе django.test.Client. Общее количество тестов достигло 28 "
        "(100% успешно пройдены);",
    )
    add_bullet(
        "Интерактивные действия и аналитика: ",
        "добавлены сводная панель кафедры, фильтры, поиск, прогресс-бар "
        "выполнения нормы и прямое действие отмены/восстановления поручений "
        "(/workloads/<id>/toggle/);",
    )
    add_bullet(
        "Обеспечена чистота кода: ",
        "проект полностью удовлетворяет стандарту PEP 8 (flake8 0 замечаний "
        "при ограничении длины строки 79 символов).",
    )

    # Раздел 5
    add_section_header("5. Вывод")
    p_concl = doc.add_paragraph()
    p_concl.paragraph_format.space_before = Pt(2)
    p_concl.paragraph_format.space_after = Pt(6)
    p_concl.paragraph_format.line_spacing = 1.15
    p_concl.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_concl = p_concl.add_run(
        "В ходе выполнения практической работы № 5 были успешно освоены "
        "фундаментальные принципы веб-разработки на Python и фреймворке "
        "Django 5.2, архитектура клиент-серверного взаимодействия и протокол "
        "HTTP. Индивидуальный проект «Система учета учебной нагрузки "
        "преподавателей» переведен на веб-ориентированную архитектуру "
        "с сохранением полной обратной совместимости с консольной "
        "версией main.py и классами предметной области. Организована "
        "чистая структура Django-приложений (homepage, teachers, "
        "workloads), настроена маршрутизация и обработка кодов состояния "
        "200 и 404. Интерфейс на базе Bootstrap 5.3 CDN предоставил "
        "наглядные карточки, бейджи, аналитику и прогресс-бар для "
        "контроля учебной нагрузки кафедры. Качество разработки подтверждено "
        "успешным прохождением 28 модульных тестов pytest и строгим "
        "соответствием стандартам PEP 8."
    )
    r_concl.font.name = "Times New Roman"

    out_path = r"C:\Users\nolik\Desktop\Отчет_ПР5.docx"
    doc.save(out_path)
    print(f"Отчет успешно сохранен: {out_path}")


if __name__ == "__main__":
    create_report()
