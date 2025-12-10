#!/usr/bin/env python3
"""
Задание 1 — парсинг дат печатных газет и вывод объектов datetime.

Программа берёт строки дат в форматах, используемых в условии задачи,
и преобразует их в объекты ``datetime.datetime``.
"""
from datetime import datetime
from datetime import timedelta


def main():
    samples = [
        ("The Moscow Times", "Wednesday, October 2, 2002"),
        ("The Guardian", "Friday, 11.10.13"),
        ("Daily News", "Thursday, 18 August 1977"),
    ]

    # Соответствующие форматы для передачи в datetime.strptime
    formats = [
        "%A, %B %d, %Y",  # Wednesday, October 2, 2002
        "%A, %d.%m.%y",   # Friday, 11.10.13 (two-digit year)
        "%A, %d %B %Y",   # Thursday, 18 August 1977
    ]

    for (paper, date_str), fmt in zip(samples, formats):
        try:
            dt = datetime.strptime(date_str, fmt)
            # Печатаем объект datetime в виде, аналогичном примеру:
            print(dt)
        except ValueError as e:
            print(f"Ошибка парсинга для '{paper}': '{date_str}' с форматом '{fmt}' — {e}")

    # --- Дополнительная функция для задания 2 ---
    def date_range(start_date, end_date):
        """Возвращает список дат в формате 'YYYY-MM-DD' от start_date до end_date включительно.

        Если формат входных данных неверный или start_date > end_date, возвращается пустой список.
        """
        fmt = "%Y-%m-%d"
        try:
            s = datetime.strptime(start_date, fmt).date()
            e = datetime.strptime(end_date, fmt).date()
        except Exception:
            return []

        if s > e:
            return []

        out = []
        cur = s
        while cur <= e:
            out.append(cur.isoformat())
            cur = cur + timedelta(days=1)

        return out

    # Примеры использования date_range
    print()
    print("Пример date_range (валидный диапазон):")
    print(date_range('2022-01-01', '2022-01-03'))

    print("\nПример date_range (start_date > end_date):")
    print(date_range('2022-01-05', '2022-01-03'))

    print("\nПример date_range (неверный формат):")
    print(date_range('2022-13-01', '2022-01-03'))


if __name__ == "__main__":
    main()
