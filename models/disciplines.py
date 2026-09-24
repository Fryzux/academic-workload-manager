from typing import Optional


class Discipline:
    """Класс, описывающий учебную дисциплину."""

    def __init__(
        self,
        discipline_id: int,
        name: str,
        department: str,
        semester: int = 1,
    ) -> None:
        """Создать объект учебной дисциплины."""
        self.id: int = int(discipline_id)
        self.name: str = name.strip()
        self.department: str = department.strip()
        self.semester: int = int(semester)

    @classmethod
    def from_data(cls, data: dict) -> "Discipline":
        """Создать объект дисциплины из словаря данных."""
        return cls(
            discipline_id=data["id"],
            name=data["name"],
            department=data["department"],
            semester=data.get("semester", 1),
        )

    @staticmethod
    def validate_semester(semester: int) -> bool:
        """Проверить корректность номера семестра."""
        return 1 <= semester <= 12

    def to_dict(self) -> dict:
        """Преобразовать объект в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "department": self.department,
            "semester": self.semester,
        }

    def __str__(self) -> str:
        """Вернуть строковое представление дисциплины."""
        return (
            f"ID {self.id}: {self.name} "
            f"({self.department}, сем. {self.semester})"
        )


def add_discipline(
    disciplines: list[Discipline],
    name: str,
    department: str,
    semester: int = 1,
) -> Discipline:
    """Создать объект Discipline и добавить его в коллекцию."""
    next_id = max((d.id for d in disciplines), default=0) + 1
    discipline = Discipline(
        discipline_id=next_id,
        name=name,
        department=department,
        semester=semester,
    )
    disciplines.append(discipline)
    return discipline


def find_disciplines(
    disciplines: list[Discipline],
    query: str,
) -> list[Discipline]:
    """Найти дисциплины по подстроке в названии или кафедре."""
    q = query.strip().lower()
    return [
        d for d in disciplines
        if q in d.name.lower() or q in d.department.lower()
    ]


def find_discipline_by_id(
    disciplines: list[Discipline],
    discipline_id: int,
) -> Optional[Discipline]:
    """Найти объект Discipline в коллекции по идентификатору."""
    for d in disciplines:
        if d.id == discipline_id:
            return d
    return None


def show_disciplines(disciplines: list[Discipline]) -> None:
    """Вывести список учебных дисциплин в виде таблицы."""
    if not disciplines:
        print("\nСписок дисциплин пуст.")
        return

    print("\n" + "=" * 75)
    print(
        f"{'ID':<4} | {'Название дисциплины':<35} | "
        f"{'Кафедра':<22} | {'Сем.':<4}"
    )
    print("-" * 75)
    for d in disciplines:
        print(
            f"{d.id:<4} | {d.name[:35]:<35} | "
            f"{d.department[:22]:<22} | {d.semester:>4}"
        )
    print("=" * 75)
