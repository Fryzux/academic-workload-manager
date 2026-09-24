from typing import Optional
from .teachers import Teacher
from .disciplines import Discipline


class Workload:
    """Класс, описывающий учебное поручение преподавателя."""

    def __init__(
        self,
        workload_id: int,
        teacher: Teacher,
        discipline: Discipline,
        lectures: float,
        practices: float,
        labs: float,
        exams: float,
        is_cancelled: bool = False,
    ) -> None:
        """Создать объект учебного поручения."""
        self.id: int = int(workload_id)
        self.teacher: Teacher = teacher
        self.discipline: Discipline = discipline
        self.lectures: float = round(float(lectures), 2)
        self.practices: float = round(float(practices), 2)
        self.labs: float = round(float(labs), 2)
        self.exams: float = round(float(exams), 2)
        self.is_cancelled: bool = bool(is_cancelled)

    @property
    def total_hours(self) -> float:
        """Суммарный объем академических часов по поручению."""
        return round(
            self.lectures + self.practices + self.labs + self.exams, 2
        )

    @property
    def status(self) -> str:
        """Текстовый статус учебного поручения."""
        return "Отменено" if self.is_cancelled else "Активно"

    def cancel(self) -> None:
        """Отменить учебное поручение."""
        self.is_cancelled = True

    def restore(self) -> None:
        """Восстановить ранее отмененное поручение."""
        self.is_cancelled = False

    def to_dict(self) -> dict:
        """Преобразовать объект в структуру данных JSON."""
        return {
            "id": self.id,
            "teacher_id": self.teacher.id,
            "discipline_id": self.discipline.id,
            "lectures": self.lectures,
            "practices": self.practices,
            "labs": self.labs,
            "exams": self.exams,
            "total_hours": self.total_hours,
            "is_cancelled": self.is_cancelled,
        }

    def __str__(self) -> str:
        """Вернуть строковое представление учебного поручения."""
        return (
            f"Поручение №{self.id} [{self.status}]: {self.teacher.name} -> "
            f"{self.discipline.name} ({self.total_hours:.1f} ч)"
        )


def calculate_total_workload(
    lecture_hours: float,
    practice_hours: float,
    lab_hours: float,
    exam_hours: float,
) -> float:
    """Расчет суммарных академических часов учебной нагрузки."""
    total = (
        float(lecture_hours)
        + float(practice_hours)
        + float(lab_hours)
        + float(exam_hours)
    )
    return round(total, 2)


def check_workload_compliance(
    total_hours: float,
    planned_hours: float,
    tolerance_hours: float = 10.0,
) -> str:
    """Проверка соответствия фактической нагрузки нормативу ставки."""
    difference = float(total_hours) - float(planned_hours)

    if abs(difference) <= float(tolerance_hours):
        return (
            f"Норма соблюдена (отклонение {difference:+.1f} ч "
            f"в пределах допуска ±{tolerance_hours:.1f} ч)"
        )
    if difference > 0:
        return f"Перегрузка (превышение нормы на {difference:.1f} ч)"
    return f"Недогрузка (дефицит объема составляет {abs(difference):.1f} ч)"


def calculate_actual_rate(
    total_hours: float,
    standard_full_rate_hours: float = 900.0,
) -> float:
    """Расчет фактической доли ставки преподавателя."""
    if standard_full_rate_hours <= 0:
        return 0.0
    actual_rate = float(total_hours) / float(standard_full_rate_hours)
    return round(actual_rate, 2)


def calculate_plan_fulfillment_percent(
    total_hours: float,
    planned_hours: float,
) -> float:
    """Расчет процента выполнения плановой нормы нагрузки."""
    if planned_hours <= 0:
        return 0.0
    percent = (float(total_hours) / float(planned_hours)) * 100.0
    return round(percent, 1)


def create_workload(
    workloads: list[Workload],
    teacher: Teacher,
    discipline: Discipline,
    lectures: float,
    practices: float,
    labs: float,
    exams: float,
) -> Optional[Workload]:
    """Создать объект Workload и добавить его в коллекцию."""
    for w in workloads:
        if (
            not w.is_cancelled
            and w.teacher.id == teacher.id
            and w.discipline.id == discipline.id
        ):
            return None

    next_id = max((item.id for item in workloads), default=0) + 1
    workload = Workload(
        workload_id=next_id,
        teacher=teacher,
        discipline=discipline,
        lectures=lectures,
        practices=practices,
        labs=labs,
        exams=exams,
        is_cancelled=False,
    )
    workloads.append(workload)
    return workload


def cancel_workload(workloads: list[Workload], workload_id: int) -> bool:
    """Отменить учебное поручение через его метод cancel()."""
    for w in workloads:
        if w.id == workload_id:
            w.cancel()
            return True
    return False


def get_teacher_workloads(
    workloads: list[Workload],
    teacher_id: int,
    include_cancelled: bool = False,
) -> list[Workload]:
    """Получить поручения преподавателя (по умолчанию только активные)."""
    return [
        w for w in workloads
        if w.teacher.id == teacher_id
        and (include_cancelled or not w.is_cancelled)
    ]


def get_teacher_total_hours(
    workloads: list[Workload],
    teacher_id: int,
) -> float:
    """Суммарные активные часы нагрузки преподавателя."""
    active_items = get_teacher_workloads(workloads, teacher_id)
    total = sum(w.total_hours for w in active_items)
    return round(total, 2)


def show_workloads(
    workloads: list[Workload],
    show_cancelled: bool = True,
) -> None:
    """Вывести список учебных поручений в виде таблицы."""
    if show_cancelled:
        items = workloads
    else:
        items = [w for w in workloads if not w.is_cancelled]
    if not items:
        print("\nСписок учебных поручений пуст.")
        return

    print("\n" + "=" * 98)
    print(
        f"{'ID':<4} | {'Преподаватель':<24} | {'Дисциплина':<30} | "
        f"{'Лек.':<5} | {'Прак.':<5} | {'Лаб.':<5} | {'Экз.':<5} | "
        f"{'Всего':<6} | {'Статус':<9}"
    )
    print("-" * 98)
    for w in items:
        print(
            f"{w.id:<4} | {w.teacher.name[:24]:<24} | "
            f"{w.discipline.name[:30]:<30} | "
            f"{w.lectures:>5.1f} | {w.practices:>5.1f} | "
            f"{w.labs:>5.1f} | {w.exams:>5.1f} | "
            f"{w.total_hours:>6.1f} | {w.status:<9}"
        )
    print("=" * 98)


def show_teacher_workload_report(
    teacher: Teacher,
    workloads: list[Workload],
    standard_full_rate_hours: float = 900.0,
) -> None:
    """Сформировать и вывести индивидуальный отчет нагрузки преподавателя."""
    t_workloads = get_teacher_workloads(workloads, teacher.id)
    total_hours = get_teacher_total_hours(workloads, teacher.id)

    contract_rate = teacher.rate
    planned_hours = teacher.calculate_planned_hours(standard_full_rate_hours)
    compliance_status = check_workload_compliance(total_hours, planned_hours)
    actual_rate = calculate_actual_rate(total_hours, standard_full_rate_hours)
    fulfillment = calculate_plan_fulfillment_percent(
        total_hours, planned_hours
    )

    print("\n" + "=" * 72)
    print("ИНДИВИДУАЛЬНЫЙ ОТЧЕТ ОБ УЧЕБНОЙ НАГРУЗКЕ ПРЕПОДАВАТЕЛЯ")
    print("=" * 72)
    print(f"ФИО:                   {teacher.name}")
    print(f"Должность:             {teacher.position}")
    print(f"Кафедра:               {teacher.department}")
    print(f"Ставка по договору:    {contract_rate:.2f}")
    print(f"Норма часов в год:     {planned_hours:.1f} ч")
    print("-" * 72)
    print("Закрепленные учебные дисциплины (активные):")
    if not t_workloads:
        print("  (нет активных учебных поручений)")
    else:
        for item in t_workloads:
            disc_info = (
                f"{item.discipline.name} (сем. {item.discipline.semester})"
            )
            print(
                f"  • {disc_info}: "
                f"Лек: {item.lectures:.1f} ч, "
                f"Прак: {item.practices:.1f} ч, "
                f"Лаб: {item.labs:.1f} ч, "
                f"Экз: {item.exams:.1f} ч "
                f"-> Итого: {item.total_hours:.1f} ч"
            )
    print("-" * 72)
    print(f"Суммарная нагрузка:    {total_hours:.1f} ч")
    print(f"Фактическая ставка:    {actual_rate:.2f}")
    print(f"Выполнение нормы:      {fulfillment:.1f} %")
    print(f"Статус проверки:       {compliance_status}")
    print("=" * 72)
