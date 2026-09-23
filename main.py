import os
from storage import (
    load_teachers,
    save_teachers,
    load_workloads,
    save_workloads,
)
from teachers import (
    add_teacher,
    find_teachers,
    get_teacher,
    filter_teachers_by_rate,
    sort_teachers,
)
from utils import (
    input_int,
    input_float,
    input_str,
)
from workloads import (
    add_workload,
    cancel_workload,
    get_teacher_workloads,
    get_teacher_total_hours,
    check_workload_compliance,
    calculate_actual_rate,
    calculate_plan_fulfillment_percent,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEACHERS_FILE = os.path.join(BASE_DIR, "data", "teachers.json")
WORKLOADS_FILE = os.path.join(BASE_DIR, "data", "workloads.json")


def show_teachers(teachers_list: list[dict]) -> None:
    """Вывести список преподавателей в виде форматированной таблицы."""
    if not teachers_list:
        print("\nСписок преподавателей пуст.")
        return

    print("\n" + "=" * 80)
    print(
        f"{'ID':<4} | {'ФИО':<28} | {'Должность':<20} | "
        f"{'Кафедра':<25} | {'Ставка':<6}"
    )
    print("-" * 80)
    for t in teachers_list:
        print(
            f"{t['id']:<4} | {t['name']:<28} | {t['position']:<20} | "
            f"{t['department']:<25} | {t['rate']:>6.2f}"
        )
    print("=" * 80)


def show_workloads(
    workloads: list[dict],
    teachers: dict[int, dict],
) -> None:
    """Вывести список всех учебных поручений в виде таблицы."""
    if not workloads:
        print("\nСписок учебных поручений пуст.")
        return

    print("\n" + "=" * 90)
    print(
        f"{'ID':<4} | {'Преподаватель':<26} | {'Дисциплина':<32} | "
        f"{'Лек.':<5} | {'Прак.':<5} | {'Лаб.':<5} | {'Экз.':<5} | "
        f"{'Всего':<6}"
    )
    print("-" * 90)
    for w in workloads:
        teacher = get_teacher(teachers, w["teacher_id"])
        teacher_name = teacher["name"] if teacher else f"ID {w['teacher_id']}"
        print(
            f"{w['id']:<4} | {teacher_name[:26]:<26} | "
            f"{w['discipline'][:32]:<32} | "
            f"{w['lectures']:>5.1f} | {w['practices']:>5.1f} | "
            f"{w['labs']:>5.1f} | {w['exams']:>5.1f} | "
            f"{w['total_hours']:>6.1f}"
        )
    print("=" * 90)


def show_teacher_workload_report(
    teacher: dict,
    workloads: list[dict],
    standard_full_rate_hours: float = 900.0,
) -> None:
    """Сформировать и вывести индивидуальный отчет о нагрузке преподавателя."""
    t_id = teacher["id"]
    t_workloads = get_teacher_workloads(workloads, t_id)
    total_hours = get_teacher_total_hours(workloads, t_id)

    contract_rate = teacher["rate"]
    planned_hours = standard_full_rate_hours * contract_rate
    compliance_status = check_workload_compliance(total_hours, planned_hours)
    actual_rate = calculate_actual_rate(total_hours, standard_full_rate_hours)
    fulfillment = calculate_plan_fulfillment_percent(
        total_hours, planned_hours
    )

    print("\n" + "=" * 70)
    print("ИНДИВИДУАЛЬНЫЙ ОТЧЕТ ОБ УЧЕБНОЙ НАГРУЗКЕ ПРЕПОДАВАТЕЛЯ")
    print("=" * 70)
    print(f"ФИО:                   {teacher['name']}")
    print(f"Должность:             {teacher['position']}")
    print(f"Кафедра:               {teacher['department']}")
    print(f"Ставка по договору:    {contract_rate:.2f}")
    print(f"Норма часов в год:     {planned_hours:.1f} ч")
    print("-" * 70)
    print("Закрепленные учебные дисциплины:")
    if not t_workloads:
        print("  (нет назначенных поручений)")
    else:
        for item in t_workloads:
            print(
                f"  • {item['discipline']}: "
                f"Лек: {item['lectures']:.1f} ч, "
                f"Прак: {item['practices']:.1f} ч, "
                f"Лаб: {item['labs']:.1f} ч, "
                f"Экз: {item['exams']:.1f} ч "
                f"-> Итого: {item['total_hours']:.1f} ч"
            )
    print("-" * 70)
    print(f"Суммарная нагрузка:    {total_hours:.1f} ч")
    print(f"Фактическая ставка:    {actual_rate:.2f}")
    print(f"Выполнение нормы:      {fulfillment:.1f} %")
    print(f"Статус проверки:       {compliance_status}")
    print("=" * 70)


def print_menu() -> None:
    """Вывести пункты главного меню программы."""
    print("\n=== СИСТЕМА УЧЕТА УЧЕБНОЙ НАГРУЗКИ (ПР2) ===")
    print("1. Показать список преподавателей")
    print("2. Найти преподавателя по ФИО или кафедре")
    print("3. Отсортировать преподавателей (lambda-сортировка)")
    print("4. Отфильтровать преподавателей по ставке (генератор)")
    print("5. Добавить нового преподавателя")
    print("6. Назначить учебную нагрузку")
    print("7. Индивидуальный отчет о нагрузке преподавателя")
    print("8. Удалить (отменить) учебную нагрузку")
    print("9. Показать все учебные поручения")
    print("0. Сохранить данные и выйти")


def main() -> None:
    """Главная функция приложения и цикл интерактивного меню."""
    teachers = load_teachers(TEACHERS_FILE)
    workloads = load_workloads(WORKLOADS_FILE)

    while True:
        print_menu()
        choice = input_int("Выберите действие (0-9): ", 0, 9)

        if choice == 1:
            show_teachers(list(teachers.values()))

        elif choice == 2:
            query = input_str("Введите подстроку для поиска: ")
            found = find_teachers(teachers, query)
            print(f"\nНайдено преподавателей: {len(found)}")
            show_teachers(found)

        elif choice == 3:
            print("\nКритерии сортировки:")
            print("1. По ФИО (по алфавиту)")
            print("2. По ставке (по убыванию)")
            sort_choice = input_int("Выберите критерий (1-2): ", 1, 2)
            sort_by = "rate" if sort_choice == 2 else "name"
            sorted_list = sort_teachers(teachers, by=sort_by)
            show_teachers(sorted_list)

        elif choice == 4:
            min_rate = input_float(
                "Введите минимальную ставку (например, 0.5): ", 0.0
            )
            filtered = filter_teachers_by_rate(teachers, min_rate)
            print(f"\nПреподаватели со ставкой >= {min_rate}: {len(filtered)}")
            show_teachers(filtered)

        elif choice == 5:
            print("\n--- Добавление нового преподавателя ---")
            name = input_str("ФИО: ")
            pos = input_str("Должность: ")
            dept = input_str("Кафедра: ")
            rate = input_float("Ставка (0.1 - 2.0): ", 0.1, 2.0)
            new_id = add_teacher(teachers, name, pos, dept, rate)
            save_teachers(TEACHERS_FILE, teachers)
            print(f"Преподаватель успешно добавлен с ID: {new_id}")

        elif choice == 6:
            print("\n--- Назначение учебной нагрузки ---")
            if not teachers:
                print("Сначала добавьте преподавателей!")
                continue
            show_teachers(list(teachers.values()))
            t_id = input_int("Введите ID преподавателя: ")
            teacher = get_teacher(teachers, t_id)
            if not teacher:
                print(f"Преподаватель с ID {t_id} не найден.")
                continue

            disc = input_str("Название дисциплины: ")
            lec = input_float("Часы лекций: ", 0.0)
            prac = input_float("Часы практических занятий: ", 0.0)
            labs = input_float("Часы лабораторных работ: ", 0.0)
            exam = input_float("Часы консультаций и экзаменов: ", 0.0)

            new_w = add_workload(
                workloads, t_id, disc, lec, prac, labs, exam
            )
            save_workloads(WORKLOADS_FILE, workloads)
            print(
                f"Нагрузка назначена (ID поручения: {new_w['id']}, "
                f"часов: {new_w['total_hours']:.1f})."
            )

        elif choice == 7:
            if not teachers:
                print("Список преподавателей пуст.")
                continue
            show_teachers(list(teachers.values()))
            t_id = input_int("Введите ID преподавателя для отчета: ")
            teacher = get_teacher(teachers, t_id)
            if not teacher:
                print(f"Преподаватель с ID {t_id} не найден.")
                continue
            show_teacher_workload_report(teacher, workloads)

        elif choice == 8:
            print("\n--- Удаление (отмена) учебной нагрузки ---")
            show_workloads(workloads, teachers)
            w_id = input_int("Введите ID поручения для удаления: ")
            if cancel_workload(workloads, w_id):
                save_workloads(WORKLOADS_FILE, workloads)
                print(f"Учебное поручение ID {w_id} успешно удалено.")
            else:
                print(f"Поручение с ID {w_id} не найдено.")

        elif choice == 9:
            show_workloads(workloads, teachers)

        elif choice == 0:
            save_teachers(TEACHERS_FILE, teachers)
            save_workloads(WORKLOADS_FILE, workloads)
            print("Данные успешно сохранены. Работа программы завершена.")
            break


if __name__ == "__main__":
    main()
