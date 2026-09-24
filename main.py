import os
from models import Teacher, Discipline, Workload
from models.teachers import (
    add_teacher,
    find_teachers,
    find_teacher_by_id,
    filter_teachers_by_rate,
    sort_teachers,
    show_teachers,
)
from models.disciplines import (
    add_discipline,
    find_discipline_by_id,
    show_disciplines,
)
from models.workloads import (
    create_workload,
    cancel_workload,
    show_workloads,
    show_teacher_workload_report,
)
from storage import (
    load_teachers,
    save_teachers,
    load_disciplines,
    save_disciplines,
    load_workloads,
    save_workloads,
)
from utils import (
    input_int,
    input_float,
    input_str,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEACHERS_FILE = os.path.join(BASE_DIR, "data", "teachers.json")
DISCIPLINES_FILE = os.path.join(BASE_DIR, "data", "disciplines.json")
WORKLOADS_FILE = os.path.join(BASE_DIR, "data", "workloads.json")


def create_new_workload(
    workloads: list[Workload],
    teachers: list[Teacher],
    disciplines: list[Discipline],
) -> None:
    """Пользовательский сценарий создания и привязки нового поручения."""
    print("\n--- Назначение учебной нагрузки ---")
    if not teachers:
        print("Ошибка: список преподавателей пуст.")
        return
    if not disciplines:
        print("Ошибка: список дисциплин пуст.")
        return

    show_teachers(teachers)
    t_id = input_int("Введите ID преподавателя: ")
    teacher = find_teacher_by_id(teachers, t_id)
    if not teacher:
        print(f"Преподаватель с ID {t_id} не найден.")
        return

    show_disciplines(disciplines)
    d_id = input_int("Введите ID дисциплины: ")
    discipline = find_discipline_by_id(disciplines, d_id)
    if not discipline:
        print(f"Дисциплина с ID {d_id} не найдена.")
        return

    lec = input_float("Часы лекций: ", 0.0)
    prac = input_float("Часы практических занятий: ", 0.0)
    labs = input_float("Часы лабораторных работ: ", 0.0)
    exam = input_float("Часы консультаций и экзаменов: ", 0.0)

    workload = create_workload(
        workloads, teacher, discipline, lec, prac, labs, exam
    )
    if workload is None:
        print(
            f"Внимание: активное поручение для преподавателя {teacher.name} "
            f"по дисциплине '{discipline.name}' уже существует."
        )
    else:
        save_workloads(WORKLOADS_FILE, workloads)
        print(
            f"Учебное поручение №{workload.id} успешно создано "
            f"(объем: {workload.total_hours:.1f} ч)."
        )


def print_menu() -> None:
    """Вывести пункты главного меню приложения."""
    print("\n=== СИСТЕМА УЧЕТА УЧЕБНОЙ НАГРУЗКИ (ПР3 - ООП) ===")
    print("1. Показать список преподавателей")
    print("2. Показать список дисциплин")
    print("3. Найти преподавателя (по ФИО / кафедре)")
    print("4. Сортировать преподавателей (lambda-сортировка)")
    print("5. Отфильтровать преподавателей по ставке (генератор)")
    print("6. Добавить преподавателя")
    print("7. Добавить учебную дисциплину")
    print("8. Назначить учебную нагрузку (связывание объектов)")
    print("9. Индивидуальный отчет о нагрузке преподавателя")
    print("10. Отменить (снять) учебную нагрузку")
    print("11. Показать все учебные поручения")
    print("0. Сохранить данные и выйти")


def main() -> None:
    """Главная функция приложения и цикл обработки операций."""
    teachers = load_teachers(TEACHERS_FILE)
    disciplines = load_disciplines(DISCIPLINES_FILE)
    workloads = load_workloads(WORKLOADS_FILE, teachers, disciplines)

    while True:
        print_menu()
        choice = input_int("Выберите действие (0-11): ", 0, 11)

        if choice == 1:
            show_teachers(teachers)

        elif choice == 2:
            show_disciplines(disciplines)

        elif choice == 3:
            query = input_str("Введите подстроку для поиска: ")
            found = find_teachers(teachers, query)
            print(f"\nНайдено преподавателей: {len(found)}")
            show_teachers(found)

        elif choice == 4:
            print("\nКритерии сортировки:")
            print("1. По ФИО (по алфавиту)")
            print("2. По ставке (по убыванию)")
            sort_choice = input_int("Выберите критерий (1-2): ", 1, 2)
            sort_by = "rate" if sort_choice == 2 else "name"
            sorted_list = sort_teachers(teachers, by=sort_by)
            show_teachers(sorted_list)

        elif choice == 5:
            min_rate = input_float(
                "Введите минимальную ставку (например, 0.5): ", 0.0
            )
            filtered = filter_teachers_by_rate(teachers, min_rate)
            print(f"\nПреподаватели со ставкой >= {min_rate}: {len(filtered)}")
            show_teachers(filtered)

        elif choice == 6:
            print("\n--- Добавление нового преподавателя ---")
            name = input_str("ФИО: ")
            pos = input_str("Должность: ")
            dept = input_str("Кафедра: ")
            rate = input_float("Ставка (0.1 - 2.0): ", 0.1, 2.0)
            if not Teacher.validate_rate(rate):
                print("Ошибка: некорректная ставка.")
                continue
            new_teacher = add_teacher(teachers, name, pos, dept, rate)
            save_teachers(TEACHERS_FILE, teachers)
            print(f"Преподаватель успешно добавлен: {new_teacher}")

        elif choice == 7:
            print("\n--- Добавление новой дисциплины ---")
            name = input_str("Название дисциплины: ")
            dept = input_str("Кафедра: ")
            sem = input_int("Семестр (1 - 12): ", 1, 12)
            new_disc = add_discipline(disciplines, name, dept, sem)
            save_disciplines(DISCIPLINES_FILE, disciplines)
            print(f"Дисциплина успешно добавлена: {new_disc}")

        elif choice == 8:
            create_new_workload(workloads, teachers, disciplines)

        elif choice == 9:
            if not teachers:
                print("Список преподавателей пуст.")
                continue
            show_teachers(teachers)
            t_id = input_int("Введите ID преподавателя для отчета: ")
            teacher = find_teacher_by_id(teachers, t_id)
            if not teacher:
                print(f"Преподаватель с ID {t_id} не найден.")
                continue
            show_teacher_workload_report(teacher, workloads)

        elif choice == 10:
            print("\n--- Отмена учебного поручения ---")
            show_workloads(workloads, show_cancelled=True)
            w_id = input_int("Введите ID поручения для отмены: ")
            if cancel_workload(workloads, w_id):
                save_workloads(WORKLOADS_FILE, workloads)
                print(
                    f"Учебное поручение №{w_id} переведено "
                    f"в статус 'Отменено'."
                )
            else:
                print(f"Поручение с ID {w_id} не найдено.")

        elif choice == 11:
            show_workloads(workloads, show_cancelled=True)

        elif choice == 0:
            save_teachers(TEACHERS_FILE, teachers)
            save_disciplines(DISCIPLINES_FILE, disciplines)
            save_workloads(WORKLOADS_FILE, workloads)
            print("Данные успешно сохранены. Работа программы завершена.")
            break


if __name__ == "__main__":
    main()
