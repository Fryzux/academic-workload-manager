from models.teachers import Teacher
from models.disciplines import Discipline
from models.workloads import (
    Workload,
    calculate_total_workload,
    check_workload_compliance,
    calculate_actual_rate,
    calculate_plan_fulfillment_percent,
    create_workload,
    cancel_workload,
    get_teacher_workloads,
    get_teacher_total_hours,
)


def test_workload_creation():
    """Проверка создания объекта Workload и связывания с Teacher."""
    teacher = Teacher(1, "Иванов И.И.", "Доцент", "ИСТ", 1.0)
    discipline = Discipline(1, "Архитектура систем", "ИСТ", 5)

    w = Workload(
        workload_id=1,
        teacher=teacher,
        discipline=discipline,
        lectures=30.0,
        practices=30.0,
        labs=60.0,
        exams=20.0,
    )
    assert w.id == 1
    assert w.teacher is teacher
    assert w.discipline is discipline
    assert w.total_hours == 140.0
    assert w.status == "Активно"
    assert w.is_cancelled is False


def test_workload_cancel_and_restore():
    """Проверка отмены и восстановления учебного поручения."""
    teacher = Teacher(1, "Петров П.П.", "Профессор", "ИП", 0.5)
    discipline = Discipline(2, "Базы данных", "ИП", 4)
    w = Workload(1, teacher, discipline, 20, 20, 40, 10)

    w.cancel()
    assert w.is_cancelled is True
    assert w.status == "Отменено"

    w.restore()
    assert w.is_cancelled is False
    assert w.status == "Активно"


def test_create_workload_and_duplicate():
    """Проверка создания поручения и блокировки дублирования активных."""
    teacher = Teacher(1, "Смирнов А.Д.", "Доцент", "ИБ", 1.0)
    discipline = Discipline(3, "Криптография", "ИБ", 6)
    workloads: list[Workload] = []

    w1 = create_workload(workloads, teacher, discipline, 30, 30, 60, 20)
    assert w1 is not None
    assert len(workloads) == 1

    # Попытка создать дублирующее активное поручение
    w2 = create_workload(workloads, teacher, discipline, 10, 10, 20, 5)
    assert w2 is None
    assert len(workloads) == 1

    # После отмены первого поручения назначение разрешено
    assert cancel_workload(workloads, 1) is True
    assert w1.is_cancelled is True

    w3 = create_workload(workloads, teacher, discipline, 10, 10, 20, 5)
    assert w3 is not None
    assert len(workloads) == 2


def test_calculations_and_compliance():
    """Проверка расчетных формул и соответствия норме ставки."""
    total = calculate_total_workload(120.0, 240.0, 360.0, 175.0)
    assert total == 895.0

    status_tol = check_workload_compliance(
        895.0, 900.0, tolerance_hours=10.0
    )
    assert "Норма соблюдена" in status_tol

    status_over = check_workload_compliance(
        950.0, 900.0, tolerance_hours=10.0
    )
    assert "Перегрузка" in status_over

    status_under = check_workload_compliance(
        800.0, 900.0, tolerance_hours=10.0
    )
    assert "Недогрузка" in status_under

    assert calculate_actual_rate(895.0, 900.0) == 0.99
    assert calculate_plan_fulfillment_percent(895.0, 900.0) == 99.4


def test_teacher_workloads_and_hours():
    """Проверка выборки активных поручений и расчета суммарных часов."""
    t1 = Teacher(1, "T1", "Доцент", "D", 1.0)
    t2 = Teacher(2, "T2", "Ассистент", "D", 0.5)
    d1 = Discipline(1, "D1", "D", 1)
    d2 = Discipline(2, "D2", "D", 2)

    workloads: list[Workload] = []
    create_workload(workloads, t1, d1, 20, 20, 20, 20)  # 80 ч
    create_workload(workloads, t1, d2, 10, 10, 10, 10)  # 40 ч
    create_workload(workloads, t2, d1, 15, 15, 15, 15)  # 60 ч

    t1_items = get_teacher_workloads(workloads, 1)
    assert len(t1_items) == 2

    t1_hours = get_teacher_total_hours(workloads, 1)
    assert t1_hours == 120.0

    # Отменяем одно поручение t1
    cancel_workload(workloads, 1)
    active_hours = get_teacher_total_hours(workloads, 1)
    assert active_hours == 40.0
