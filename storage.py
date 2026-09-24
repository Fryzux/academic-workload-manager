import json
import os
from models.teachers import Teacher, find_teacher_by_id
from models.disciplines import Discipline, find_discipline_by_id
from models.workloads import Workload


def load_teachers(filepath: str) -> list[Teacher]:
    """Загрузить коллекцию объектов Teacher из JSON-файла."""
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            raw_data = json.load(file)
            if not isinstance(raw_data, list):
                return []
            return [Teacher.from_data(item) for item in raw_data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_teachers(filepath: str, teachers: list[Teacher]) -> None:
    """Сохранить коллекцию объектов Teacher в JSON-файл."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    data = [t.to_dict() for t in teachers]
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_disciplines(filepath: str) -> list[Discipline]:
    """Загрузить коллекцию объектов Discipline из JSON-файла."""
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            raw_data = json.load(file)
            if not isinstance(raw_data, list):
                return []
            return [Discipline.from_data(item) for item in raw_data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_disciplines(filepath: str, disciplines: list[Discipline]) -> None:
    """Сохранить коллекцию объектов Discipline в JSON-файл."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    data = [d.to_dict() for d in disciplines]
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_workloads(
    filepath: str,
    teachers: list[Teacher],
    disciplines: list[Discipline],
) -> list[Workload]:
    """Загрузить поручения из JSON с восстановлением объектных связей."""
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            raw_data = json.load(file)
            if not isinstance(raw_data, list):
                return []

            workloads: list[Workload] = []
            for item in raw_data:
                teacher = find_teacher_by_id(teachers, item["teacher_id"])
                discipline = find_discipline_by_id(
                    disciplines, item["discipline_id"]
                )
                if teacher and discipline:
                    workload = Workload(
                        workload_id=item["id"],
                        teacher=teacher,
                        discipline=discipline,
                        lectures=item.get("lectures", 0.0),
                        practices=item.get("practices", 0.0),
                        labs=item.get("labs", 0.0),
                        exams=item.get("exams", 0.0),
                        is_cancelled=item.get("is_cancelled", False),
                    )
                    workloads.append(workload)
            return workloads
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_workloads(filepath: str, workloads: list[Workload]) -> None:
    """Сохранить коллекцию объектов Workload в JSON-файл."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    data = [w.to_dict() for w in workloads]
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
