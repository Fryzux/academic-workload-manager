import json
import os


def load_teachers(filepath: str) -> dict[int, dict]:
    """Загрузить словарь преподавателей из JSON-файла."""
    if not os.path.exists(filepath):
        return {}

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            raw_data = json.load(file)
            teachers = {}
            if isinstance(raw_data, list):
                for item in raw_data:
                    teacher_id = int(item["id"])
                    teachers[teacher_id] = item
            elif isinstance(raw_data, dict):
                for key, item in raw_data.items():
                    teachers[int(key)] = item
            return teachers
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_teachers(filepath: str, teachers: dict[int, dict]) -> None:
    """Сохранить словарь преподавателей в JSON-файл."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    teachers_list = list(teachers.values())
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(teachers_list, file, ensure_ascii=False, indent=2)


def load_workloads(filepath: str) -> list[dict]:
    """Загрузить список учебных поручений из JSON-файла."""
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
            return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_workloads(filepath: str, workloads: list[dict]) -> None:
    """Сохранить список учебных поручений в JSON-файл."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(workloads, file, ensure_ascii=False, indent=2)
