from models.disciplines import (
    Discipline,
    add_discipline,
    find_disciplines,
    find_discipline_by_id,
)


def test_discipline_creation():
    """Проверка создания объекта Discipline и его атрибутов."""
    d = Discipline(
        discipline_id=1,
        name="Архитектура программных систем",
        department="ИСТ",
        semester=5,
    )
    assert d.id == 1
    assert d.name == "Архитектура программных систем"
    assert d.department == "ИСТ"
    assert d.semester == 5


def test_discipline_str():
    """Проверка строкового представления объекта Discipline."""
    d = Discipline(2, "Базы данных", "ИП", 4)
    text = str(d)
    assert "Базы данных" in text
    assert "ИП" in text
    assert "сем. 4" in text


def test_discipline_validate_semester():
    """Проверка статического метода валидации семестра."""
    assert Discipline.validate_semester(1) is True
    assert Discipline.validate_semester(12) is True
    assert Discipline.validate_semester(0) is False
    assert Discipline.validate_semester(13) is False


def test_discipline_from_data():
    """Проверка создания объекта Discipline из словаря JSON."""
    data = {
        "id": 10,
        "name": "Информатика",
        "department": "ИСТ",
        "semester": 1,
    }
    d = Discipline.from_data(data)
    assert isinstance(d, Discipline)
    assert d.id == 10
    assert d.name == "Информатика"
    assert d.to_dict()["semester"] == 1


def test_add_and_find_disciplines():
    """Проверка добавления и поиска объектов Discipline в коллекции."""
    disciplines: list[Discipline] = []
    d1 = add_discipline(disciplines, "Операционные системы", "ИП", 3)
    d2 = add_discipline(disciplines, "Сети ЭВМ", "ИСТ", 4)

    assert len(disciplines) == 2
    assert d1.id == 1
    assert d2.id == 2

    found = find_disciplines(disciplines, "сети")
    assert len(found) == 1
    assert found[0].id == 2

    by_id = find_discipline_by_id(disciplines, 1)
    assert by_id is not None
    assert by_id.name == "Операционные системы"

    not_found = find_discipline_by_id(disciplines, 999)
    assert not_found is None
