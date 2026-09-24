from typing import Iterator, Optional


class Teacher:
    """Класс, описывающий преподавателя кафедры."""

    def __init__(
        self,
        teacher_id: int,
        name: str,
        position: str,
        department: str,
        rate: float = 1.0,
    ) -> None:
        """Создать объект преподавателя."""
        self.id: int = int(teacher_id)
        self.name: str = name.strip()
        self.position: str = position.strip()
        self.department: str = department.strip()
        self.rate: float = round(float(rate), 2)

    @classmethod
    def from_data(cls, data: dict) -> "Teacher":
        """Создать объект преподавателя из словаря данных."""
        return cls(
            teacher_id=data["id"],
            name=data["name"],
            position=data["position"],
            department=data["department"],
            rate=data.get("rate", 1.0),
        )

    @staticmethod
    def validate_rate(rate: float) -> bool:
        """Проверить корректность значения занимаемой ставки."""
        return 0.1 <= rate <= 2.0

    def calculate_planned_hours(
        self,
        standard_full_rate_hours: float = 900.0,
    ) -> float:
        """Рассчитать плановую норму часов для ставки преподавателя."""
        return round(self.rate * standard_full_rate_hours, 2)

    def to_dict(self) -> dict:
        """Преобразовать объект в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "position": self.position,
            "department": self.department,
            "rate": self.rate,
        }

    def __str__(self) -> str:
        """Вернуть строковое представление преподавателя."""
        return (
            f"ID {self.id}: {self.name}, {self.position} "
            f"({self.department}), {self.rate:.2f} ст."
        )


def add_teacher(
    teachers: list[Teacher],
    name: str,
    position: str,
    department: str,
    rate: float = 1.0,
) -> Teacher:
    """Создать объект Teacher и добавить его в коллекцию."""
    next_id = max((t.id for t in teachers), default=0) + 1
    teacher = Teacher(
        teacher_id=next_id,
        name=name,
        position=position,
        department=department,
        rate=rate,
    )
    teachers.append(teacher)
    return teacher


def find_teachers(teachers: list[Teacher], query: str) -> list[Teacher]:
    """Найти преподавателей по подстроке в ФИО или названии кафедры."""
    q = query.strip().lower()
    return [
        t for t in teachers
        if q in t.name.lower() or q in t.department.lower()
    ]


def find_teacher_by_id(
    teachers: list[Teacher],
    teacher_id: int,
) -> Optional[Teacher]:
    """Найти объект Teacher в коллекции по идентификатору."""
    for t in teachers:
        if t.id == teacher_id:
            return t
    return None


def filter_teachers_generator(
    teachers: list[Teacher],
    min_rate: float,
) -> Iterator[Teacher]:
    """Генератор отбора преподавателей со ставкой не ниже min_rate."""
    for t in teachers:
        if t.rate >= min_rate:
            yield t


def filter_teachers_by_rate(
    teachers: list[Teacher],
    min_rate: float,
) -> list[Teacher]:
    """Отобрать преподавателей по минимальной ставке с помощью генератора."""
    return list(filter_teachers_generator(teachers, min_rate))


def sort_teachers(
    teachers: list[Teacher],
    by: str = "name",
) -> list[Teacher]:
    """Отсортировать коллекцию преподавателей с использованием lambda."""
    if by == "rate":
        return sorted(teachers, key=lambda t: t.rate, reverse=True)
    return sorted(teachers, key=lambda t: t.name.lower())


def show_teachers(teachers: list[Teacher]) -> None:
    """Вывести список объектов Teacher в виде форматированной таблицы."""
    if not teachers:
        print("\nСписок преподавателей пуст.")
        return

    print("\n" + "=" * 80)
    print(
        f"{'ID':<4} | {'ФИО':<28} | {'Должность':<20} | "
        f"{'Кафедра':<25} | {'Ставка':<6}"
    )
    print("-" * 80)
    for t in teachers:
        print(
            f"{t.id:<4} | {t.name:<28} | {t.position:<20} | "
            f"{t.department:<25} | {t.rate:>6.2f}"
        )
    print("=" * 80)
