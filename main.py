from datetime import date


def calculate_total_workload(
    lecture_hours: float,
    practice_hours: float,
    lab_hours: float,
    exam_hours: float,
) -> float:
    total = float(lecture_hours) + float(practice_hours) + float(lab_hours) + float(exam_hours)
    return round(total, 2)


def check_workload_compliance(
    total_hours: float,
    planned_hours: float,
    tolerance_hours: float = 10.0,
) -> str:
    difference = float(total_hours) - float(planned_hours)

    if abs(difference) <= float(tolerance_hours):
        status = f"Норма соблюдена (отклонение {difference:+.1f} ч в пределах допуска ±{tolerance_hours:.1f} ч)"
    elif difference > 0:
        status = f"Перегрузка (превышение нормы на {difference:.1f} ч)"
    else:
        status = f"Недогрузка (дефицит объема нагрузки составляет {abs(difference):.1f} ч)"

    return status


def calculate_actual_rate(
    total_hours: float,
    standard_full_rate_hours: float = 900.0,
) -> float:
    actual_rate = float(total_hours) / float(standard_full_rate_hours)
    return round(actual_rate, 2)


def calculate_plan_fulfillment_percent(
    total_hours: float,
    planned_hours: float,
) -> float:
    fulfillment_percent = (float(total_hours) / float(planned_hours)) * 100.0
    return round(fulfillment_percent, 1)


def run_workload_report() -> None:
    teacher_name = "Иванов Иван Иванович"
    position = "Доцент"
    department = "Информационные системы и технологии"
    discipline_name = "Архитектура программных систем"
    academic_year = 2026
    report_date = date(2026, 9, 17)

    standard_full_rate_hours = 900.0
    contract_rate = 1.0
    planned_hours = standard_full_rate_hours * contract_rate

    lecture_hours = 120.0
    practice_hours = 240.0
    lab_hours = 360.0
    exam_hours = 175.0

    total_hours = calculate_total_workload(
        lecture_hours, practice_hours, lab_hours, exam_hours
    )
    compliance_status = check_workload_compliance(
        total_hours, planned_hours, tolerance_hours=10.0
    )
    actual_rate = calculate_actual_rate(total_hours, standard_full_rate_hours)
    fulfillment_percent = calculate_plan_fulfillment_percent(total_hours, planned_hours)
    is_rate_matched = (contract_rate == actual_rate)

    print("=" * 65)
    print("СИСТЕМА УЧЕТА УЧЕБНОЙ НАГРУЗКИ ПРЕПОДАВАТЕЛЕЙ")
    print("Отчет об индивидуальной учебной нагрузке")
    print(f"Дата формирования: {report_date}")
    print("=" * 65)
    print(f"Преподаватель:                     {teacher_name}")
    print(f"Должность:                         {position}")
    print(f"Кафедра:                           {department}")
    print(f"Дисциплина:                        {discipline_name}")
    print(f"Учебный год:                       {academic_year} / {academic_year + 1}")
    print("-" * 65)
    print("Распределение учебных часов:")
    print(f"  • Лекции:                          {lecture_hours:>6.1f} ч")
    print(f"  • Практические занятия:            {practice_hours:>6.1f} ч")
    print(f"  • Лабораторные работы:             {lab_hours:>6.1f} ч")
    print(f"  • Консультации и экзамены:         {exam_hours:>6.1f} ч")
    print("-" * 65)
    print(f"Суммарная нагрузка:                  {total_hours:>6.1f} ч")
    print(f"Плановая норма по договору ({contract_rate:.2f} ст.): {planned_hours:>6.1f} ч")
    print(f"Фактическая рассчитанная ставка:     {actual_rate:>6.2f} ст.")
    print(f"Процент выполнения нормы:            {fulfillment_percent:>6.1f} %")
    print(f"Точное совпадение ставки (bool):     {is_rate_matched}")
    print(f"Статус проверки:                     {compliance_status}")
    print("=" * 65)


if __name__ == "__main__":
    run_workload_report()
