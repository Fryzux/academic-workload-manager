from models.teachers import (
    Teacher,
    add_teacher,
    find_teachers,
    find_teacher_by_id,
    filter_teachers_by_rate,
    sort_teachers,
)


def test_teacher_creation():
    """Проверка создания объекта Teacher и значений его атрибутов."""
    teacher = Teacher(
        teacher_id=1,
        name="Иванов Иван Иванович",
        position="Доцент",
        department="ИСТ",
        rate=1.0,
    )
    assert teacher.id == 1
    assert teacher.name == "Иванов Иван Иванович"
    assert teacher.position == "Доцент"
    assert teacher.department == "ИСТ"
    assert teacher.rate == 1.0


def test_teacher_str():
    """Проверка строкового представления объекта Teacher."""
    teacher = Teacher(1, "Петров Петр", "Профессор", "ИП", 0.5)
    text = str(teacher)
    assert "Петров Петр" in text
    assert "Профессор" in text
    assert "0.50" in text


def test_teacher_validate_rate():
    """Проверка статического метода валидации ставки."""
    assert Teacher.validate_rate(1.0) is True
    assert Teacher.validate_rate(0.5) is True
    assert Teacher.validate_rate(0.0) is False
    assert Teacher.validate_rate(2.5) is False


def test_teacher_from_data():
    """Проверка фабричного метода создания Teacher из словаря."""
    data = {
        "id": 5,
        "name": "Сидоров С.С.",
        "position": "Ассистент",
        "department": "ИБ",
        "rate": 0.25,
    }
    t = Teacher.from_data(data)
    assert isinstance(t, Teacher)
    assert t.id == 5
    assert t.rate == 0.25
    assert t.calculate_planned_hours(900.0) == 225.0


def test_add_and_find_teachers():
    """Проверка добавления и поиска объектов Teacher в коллекции."""
    teachers: list[Teacher] = []
    t1 = add_teacher(teachers, "Алексеев А.А.", "Доцент", "Каф1", 1.0)
    t2 = add_teacher(teachers, "Борисов Б.Б.", "Профессор", "Каф2", 0.5)

    assert len(teachers) == 2
    assert t1.id == 1
    assert t2.id == 2

    found = find_teachers(teachers, "борис")
    assert len(found) == 1
    assert found[0].id == 2

    by_id = find_teacher_by_id(teachers, 1)
    assert by_id is not None
    assert by_id.name == "Алексеев А.А."

    not_found = find_teacher_by_id(teachers, 999)
    assert not_found is None


def test_filter_and_sort_teachers():
    """Проверка фильтрации генератором и lambda-сортировки."""
    teachers = [
        Teacher(1, "Яковлев", "Доцент", "К1", 0.5),
        Teacher(2, "Алексеев", "Профессор", "К2", 1.0),
        Teacher(3, "Борисов", "Ассистент", "К1", 0.25),
    ]

    filtered = filter_teachers_by_rate(teachers, 0.5)
    rates = [t.rate for t in filtered]
    assert 1.0 in rates
    assert 0.5 in rates
    assert 0.25 not in rates

    sorted_name = sort_teachers(teachers, by="name")
    assert sorted_name[0].name == "Алексеев"
    assert sorted_name[2].name == "Яковлев"

    sorted_rate = sort_teachers(teachers, by="rate")
    assert sorted_rate[0].rate == 1.0
    assert sorted_rate[2].rate == 0.25
