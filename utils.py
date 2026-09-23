def input_int(
    prompt: str,
    min_val: int | None = None,
    max_val: int | None = None,
) -> int:
    """Запросить у пользователя целое число с обработкой ошибок."""
    while True:
        raw_val = input(prompt).strip()
        try:
            val = int(raw_val)
            if min_val is not None and val < min_val:
                print(f"Значение должно быть не меньше {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"Значение должно быть не больше {max_val}.")
                continue
            return val
        except ValueError:
            print("Ошибка: введите корректное целое число.")


def input_float(
    prompt: str,
    min_val: float | None = None,
    max_val: float | None = None,
) -> float:
    """Запросить у пользователя вещественное число с обработкой ошибок."""
    while True:
        raw_val = input(prompt).strip().replace(",", ".")
        try:
            val = float(raw_val)
            if min_val is not None and val < min_val:
                print(f"Значение должно быть не меньше {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"Значение должно быть не больше {max_val}.")
                continue
            return val
        except ValueError:
            print("Ошибка: введите корректное число.")


def input_str(prompt: str) -> str:
    """Запросить непустую строку у пользователя."""
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("Ошибка: строка не может быть пустой.")
