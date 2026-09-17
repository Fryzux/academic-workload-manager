import pytest
from main import (
    calculate_total_workload,
    check_workload_compliance,
    calculate_actual_rate,
    calculate_plan_fulfillment_percent,
)


def test_calculate_total_workload_standard():
    total = calculate_total_workload(120.0, 240.0, 360.0, 175.0)
    assert total == 895.0


def test_calculate_total_workload_zeros():
    total = calculate_total_workload(0, 0, 0, 0)
    assert total == 0.0


def test_check_workload_compliance_exact():
    status = check_workload_compliance(900.0, 900.0, tolerance_hours=10.0)
    assert "Норма соблюдена" in status
    assert "+0.0" in status or "0.0" in status


def test_check_workload_compliance_within_tolerance():
    status_minus = check_workload_compliance(895.0, 900.0, tolerance_hours=10.0)
    assert "Норма соблюдена" in status_minus
    assert "-5.0" in status_minus

    status_plus = check_workload_compliance(908.0, 900.0, tolerance_hours=10.0)
    assert "Норма соблюдена" in status_plus
    assert "+8.0" in status_plus


def test_check_workload_compliance_overload():
    status = check_workload_compliance(950.0, 900.0, tolerance_hours=10.0)
    assert "Перегрузка" in status
    assert "50.0" in status


def test_check_workload_compliance_underload():
    status = check_workload_compliance(820.0, 900.0, tolerance_hours=10.0)
    assert "Недогрузка" in status
    assert "80.0" in status


def test_calculate_actual_rate():
    assert calculate_actual_rate(900.0, standard_full_rate_hours=900.0) == 1.0
    assert calculate_actual_rate(450.0, standard_full_rate_hours=900.0) == 0.5
    assert calculate_actual_rate(895.0, standard_full_rate_hours=900.0) == 0.99


def test_calculate_plan_fulfillment_percent():
    percent = calculate_plan_fulfillment_percent(895.0, 900.0)
    assert percent == 99.4

    percent_full = calculate_plan_fulfillment_percent(900.0, 900.0)
    assert percent_full == 100.0
