from teachers import (
    add_teacher,
    find_teachers,
    get_teacher,
    filter_teachers_by_rate,
    sort_teachers,
)


def test_add_teacher():
    teachers = {}
    new_id = add_teacher(
        teachers, "Сидоров Петр", "Доцент", "ИТ", rate=1.0
    )
    assert new_id == 1
    assert len(teachers) == 1
    assert teachers[1]["name"] == "Сидоров Петр"
    assert teachers[1]["rate"] == 1.0


def test_find_teachers():
    teachers = {
        1: {
            "id": 1,
            "name": "Иванов Иван",
            "position": "Профессор",
            "department": "ИСТ",
            "rate": 1.0,
        },
        2: {
            "id": 2,
            "name": "Петров Петр",
            "position": "Доцент",
            "department": "ИП",
            "rate": 0.5,
        },
    }
    found = find_teachers(teachers, "иван")
    assert len(found) == 1
    assert found[0]["id"] == 1

    found_dept = find_teachers(teachers, "ИП")
    assert len(found_dept) == 1
    assert found_dept[0]["id"] == 2


def test_get_teacher():
    teachers = {
        1: {
            "id": 1,
            "name": "Иванов Иван",
            "position": "Профессор",
            "department": "ИСТ",
            "rate": 1.0,
        }
    }
    teacher = get_teacher(teachers, 1)
    assert teacher is not None
    assert teacher["name"] == "Иванов Иван"

    not_found = get_teacher(teachers, 999)
    assert not_found is None


def test_filter_teachers_by_rate():
    teachers = {
        1: {"id": 1, "name": "A", "department": "D1", "rate": 1.0},
        2: {"id": 2, "name": "B", "department": "D2", "rate": 0.5},
        3: {"id": 3, "name": "C", "department": "D3", "rate": 0.25},
    }
    filtered = filter_teachers_by_rate(teachers, 0.5)
    rates = [t["rate"] for t in filtered]
    assert 1.0 in rates
    assert 0.5 in rates
    assert 0.25 not in rates


def test_sort_teachers():
    teachers = {
        1: {"id": 1, "name": "Яковлев", "department": "D", "rate": 0.5},
        2: {"id": 2, "name": "Алексеев", "department": "D", "rate": 1.0},
        3: {"id": 3, "name": "Борисов", "department": "D", "rate": 0.25},
    }
    by_name = sort_teachers(teachers, by="name")
    assert by_name[0]["name"] == "Алексеев"
    assert by_name[1]["name"] == "Борисов"
    assert by_name[2]["name"] == "Яковлев"

    by_rate = sort_teachers(teachers, by="rate")
    assert by_rate[0]["rate"] == 1.0
    assert by_rate[1]["rate"] == 0.5
    assert by_rate[2]["rate"] == 0.25
