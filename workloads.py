def calculate_total_workload(
    lecture_hours: float,
    practice_hours: float,
    lab_hours: float,
    exam_hours: float,
) -> float:
    """Расчет суммарных академических часов учебной нагрузки."""
    total = (
        float(lecture_hours)
        + float(practice_hours)
        + float(lab_hours)
        + float(exam_hours)
    )
    return round(total, 2)


def check_workload_compliance(
    total_hours: float,
    planned_hours: float,
    tolerance_hours: float = 10.0,
) -> str:
    """Проверка соответствия фактической нагрузки нормативу ставки."""
    difference = float(total_hours) - float(planned_hours)

    if abs(difference) <= float(tolerance_hours):
        return (
            f"Норма соблюдена (отклонение {difference:+.1f} ч "
            f"в пределах допуска ±{tolerance_hours:.1f} ч)"
        )
    if difference > 0:
        return f"Перегрузка (превышение нормы на {difference:.1f} ч)"
    return f"Недогрузка (дефицит объема составляет {abs(difference):.1f} ч)"


def calculate_actual_rate(
    total_hours: float,
    standard_full_rate_hours: float = 900.0,
) -> float:
    """Расчет фактической доли ставки преподавателя."""
    if standard_full_rate_hours <= 0:
        return 0.0
    actual_rate = float(total_hours) / float(standard_full_rate_hours)
    return round(actual_rate, 2)


def calculate_plan_fulfillment_percent(
    total_hours: float,
    planned_hours: float,
) -> float:
    """Расчет процента выполнения плановой нормы нагрузки."""
    if planned_hours <= 0:
        return 0.0
    percent = (float(total_hours) / float(planned_hours)) * 100.0
    return round(percent, 1)


def add_workload(
    workloads: list[dict],
    teacher_id: int,
    discipline: str,
    lectures: float,
    practices: float,
    labs: float,
    exams: float,
) -> dict:
    """Создать и добавить учебное поручение в список workloads."""
    next_id = max((item["id"] for item in workloads), default=0) + 1
    total_hours = calculate_total_workload(lectures, practices, labs, exams)
    assignment = {
        "id": next_id,
        "teacher_id": int(teacher_id),
        "discipline": discipline.strip(),
        "lectures": round(float(lectures), 2),
        "practices": round(float(practices), 2),
        "labs": round(float(labs), 2),
        "exams": round(float(exams), 2),
        "total_hours": total_hours,
    }
    workloads.append(assignment)
    return assignment


def cancel_workload(workloads: list[dict], workload_id: int) -> bool:
    """Отменить (удалить) учебное поручение по его идентификатору."""
    for i, item in enumerate(workloads):
        if item["id"] == workload_id:
            del workloads[i]
            return True
    return False


def get_teacher_workloads(
    workloads: list[dict],
    teacher_id: int,
) -> list[dict]:
    """Получить список учебных поручений конкретного преподавателя."""
    return [item for item in workloads if item["teacher_id"] == teacher_id]


def get_teacher_total_hours(
    workloads: list[dict],
    teacher_id: int,
) -> float:
    """Вычислить суммарные часы нагрузки преподавателя по всем поручениям."""
    teacher_items = get_teacher_workloads(workloads, teacher_id)
    total = sum(item["total_hours"] for item in teacher_items)
    return round(total, 2)
