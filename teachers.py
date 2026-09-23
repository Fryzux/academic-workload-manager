from typing import Iterator


def add_teacher(
    teachers: dict[int, dict],
    name: str,
    position: str,
    department: str,
    rate: float = 1.0,
) -> int:
    """Добавить преподавателя в словарь teachers."""
    next_id = max(teachers.keys(), default=0) + 1
    teachers[next_id] = {
        "id": next_id,
        "name": name,
        "position": position,
        "department": department,
        "rate": round(float(rate), 2),
    }
    return next_id


def find_teachers(teachers: dict[int, dict], query: str) -> list[dict]:
    """Найти преподавателей по подстроке в ФИО или кафедре."""
    q = query.strip().lower()
    result = []
    for teacher in teachers.values():
        name_match = q in teacher["name"].lower()
        dept_match = q in teacher["department"].lower()
        if name_match or dept_match:
            result.append(teacher)
    return result


def get_teacher(teachers: dict[int, dict], teacher_id: int) -> dict | None:
    """Получить данные преподавателя по идентификатору."""
    return teachers.get(teacher_id)


def filter_teachers_generator(
    teachers: dict[int, dict],
    min_rate: float,
) -> Iterator[dict]:
    """Генератор для отбора преподавателей с заданной минимальной ставкой."""
    for teacher in teachers.values():
        if teacher["rate"] >= min_rate:
            yield teacher


def filter_teachers_by_rate(
    teachers: dict[int, dict],
    min_rate: float,
) -> list[dict]:
    """Отобрать преподавателей по минимальной ставке с помощью генератора."""
    return list(filter_teachers_generator(teachers, min_rate))


def sort_teachers(
    teachers: dict[int, dict],
    by: str = "name",
) -> list[dict]:
    """Отсортировать преподавателей с использованием lambda-функции."""
    teachers_list = list(teachers.values())
    if by == "rate":
        return sorted(teachers_list, key=lambda t: t["rate"], reverse=True)
    return sorted(teachers_list, key=lambda t: t["name"].lower())
