from workloads import (
    calculate_total_workload,
    check_workload_compliance,
    calculate_actual_rate,
    calculate_plan_fulfillment_percent,
    add_workload,
    cancel_workload,
    get_teacher_workloads,
    get_teacher_total_hours,
)


def test_calculate_total_workload():
    total = calculate_total_workload(120.0, 240.0, 360.0, 175.0)
    assert total == 895.0


def test_check_workload_compliance():
    # Точное соответствие
    status_exact = check_workload_compliance(900.0, 900.0)
    assert "Норма соблюдена" in status_exact

    # В пределах допуска (-5 ч при допуске ±10 ч)
    status_tol = check_workload_compliance(895.0, 900.0, tolerance_hours=10.0)
    assert "Норма соблюдена" in status_tol

    # Перегрузка
    status_over = check_workload_compliance(950.0, 900.0, tolerance_hours=10.0)
    assert "Перегрузка" in status_over

    # Недогрузка
    status_under = check_workload_compliance(
        800.0, 900.0, tolerance_hours=10.0
    )
    assert "Недогрузка" in status_under


def test_calculate_actual_rate_and_fulfillment():
    rate = calculate_actual_rate(895.0, standard_full_rate_hours=900.0)
    assert rate == 0.99

    fulfillment = calculate_plan_fulfillment_percent(895.0, 900.0)
    assert fulfillment == 99.4


def test_add_and_cancel_workload():
    workloads = []
    w1 = add_workload(
        workloads,
        teacher_id=1,
        discipline="Информатика",
        lectures=30.0,
        practices=30.0,
        labs=60.0,
        exams=20.0,
    )
    assert w1["id"] == 1
    assert w1["total_hours"] == 140.0
    assert len(workloads) == 1

    t_workloads = get_teacher_workloads(workloads, teacher_id=1)
    assert len(t_workloads) == 1

    total_hours = get_teacher_total_hours(workloads, teacher_id=1)
    assert total_hours == 140.0

    canceled = cancel_workload(workloads, workload_id=1)
    assert canceled is True
    assert len(workloads) == 0

    canceled_non_existent = cancel_workload(workloads, workload_id=999)
    assert canceled_non_existent is False
