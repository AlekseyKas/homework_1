"""Реализация классов Account и CreditAccount для задания HW5.

Файл переименован в `script.py` по запросу студента.
Содержит те же классы и логику, что и предыдущий `solution_task_1.py`.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Any


class Account:
    """Базовый банковский счёт с ведением истории операций.

    Атрибуты:
    - holder: публичное имя владельца
    - _balance: приватный баланс (float)
    - operations_history: список словарей с записями операций
    """

    def __init__(self, account_holder: str, balance: float = 0.0) -> None:
        # Проверяем корректность имени владельца
        if not isinstance(account_holder, str) or not account_holder:
            raise ValueError("account_holder must be a non-empty string")
        # Баланс для обычного счёта не может быть отрицательным
        if balance < 0:
            raise ValueError("Initial balance for Account cannot be negative")

        self.holder: str = account_holder
        self._balance: float = float(balance)
        self.operations_history: List[Dict[str, Any]] = []

    def _now(self) -> str:
        """Возвращает текущее время в ISO-формате (строка)."""
        return datetime.now().isoformat()

    def _record(self, op_type: str, amount: float, status: str, used_credit: bool | None = None) -> None:
        """Добавляет запись об операции в `operations_history`.

        Поля записи:
        - type: тип операции ('deposit' или 'withdraw')
        - amount: сумма операции (float)
        - datetime: время операции (ISO строка)
        - balance: баланс после операции (float)
        - status: 'success' или 'fail'
        - used_credit: (опционально) булево, использован ли кредит (для CreditAccount)
        """
        entry: Dict[str, Any] = {
            "type": op_type,
            "amount": float(amount),
            "datetime": self._now(),
            "balance": float(self._balance),
            "status": status,
        }
        # Ключ used_credit добавляем только при наличии значения
        if used_credit is not None:
            entry["used_credit"] = bool(used_credit)

        self.operations_history.append(entry)

    def deposit(self, amount: float) -> None:
        """Пополнение счёта положительной суммой.

        В случае некорректной суммы (нечисло или не > 0) операция фиксируется как 'fail' и выбрасывает ValueError.
        """
        try:
            amount = float(amount)
        except Exception:
            self._record("deposit", amount, "fail")
            raise ValueError("Amount must be a number")

        if amount <= 0:
            # некорректная сумма пополнения
            self._record("deposit", amount, "fail")
            raise ValueError("Deposit amount must be positive")

        self._balance += amount
        self._record("deposit", amount, "success")

    def withdraw(self, amount: float) -> None:
        """Снятие положительной суммы при достаточном балансе.

        Попытки снятия при недостатке средств фиксируются как 'fail' и вызывают ValueError.
        """
        try:
            amount = float(amount)
        except Exception:
            self._record("withdraw", amount, "fail")
            raise ValueError("Amount must be a number")

        if amount <= 0:
            self._record("withdraw", amount, "fail")
            raise ValueError("Withdraw amount must be positive")

        if amount > self._balance:
            # недостаточно средств на обычном счёте
            self._record("withdraw", amount, "fail")
            raise ValueError("Insufficient funds")

        self._balance -= amount
        self._record("withdraw", amount, "success")

    def get_balance(self) -> float:
        """Возвращает текущий баланс (float)."""
        return float(self._balance)

    def get_history(self) -> List[Dict[str, Any]]:
        """Возвращает копию истории операций.

        Каждая запись — словарь с ключами, описанными в `_record`.
        """
        return list(self.operations_history)


class CreditAccount(Account):
    """Кредитный счёт с возможностью уходить в минус до заданного лимита.

    Дополнительный атрибут:
    - credit_limit: неотрицательное число, максимальный доступный овердрафт

    Поведение:
    - баланс может быть отрицательным, но не ниже -credit_limit
    - в истории операций фиксируется поле `used_credit` (булево)
    - есть метод `get_available_credit` — сколько ещё можно использовать кредитных средств
    """

    def __init__(self, account_holder: str, balance: float = 0.0, credit_limit: float = 0.0) -> None:
        try:
            credit_limit = float(credit_limit)
        except Exception:
            raise ValueError("credit_limit must be a number")

        if credit_limit < 0:
            raise ValueError("credit_limit must be non-negative")

        # начальный баланс разрешён до -credit_limit
        if balance < -credit_limit:
            raise ValueError("Initial balance cannot be below -credit_limit")

        # вызываем базовый конструктор; если начальный баланс отрицательный, скорректируем ниже
        super().__init__(account_holder, balance=balance if balance >= 0 else 0.0)
        if balance < 0:
            self._balance = float(balance)

        self.credit_limit: float = float(credit_limit)

    def get_available_credit(self) -> float:
        """Возвращает доступный остаток кредитных средств: balance + credit_limit."""
        return float(self._balance + self.credit_limit)

    def deposit(self, amount: float) -> None:
        # Поведение пополнения такое же, как у базового счёта, но добавляем информацию, использован ли кредит
        prev_balance = float(self._balance)
        super().deposit(amount)
        used_credit = self._balance < 0 or prev_balance < 0
        # обновляем последний элемент истории, добавляя поле used_credit
        if self.operations_history:
            self.operations_history[-1]["used_credit"] = bool(used_credit)

    def withdraw(self, amount: float) -> None:
        try:
            amount = float(amount)
        except Exception:
            # фиксируем неудачную попытку и информируем об ошибке
            self._record("withdraw", amount, "fail", used_credit=None)
            raise ValueError("Amount must be a number")

        if amount <= 0:
            self._record("withdraw", amount, "fail", used_credit=None)
            raise ValueError("Withdraw amount must be positive")

        # разрешено снимать до баланса + кредитного лимита
        if amount > (self._balance + self.credit_limit):
            # превышение доступного кредитного лимита
            self._record("withdraw", amount, "fail", used_credit=None)
            raise ValueError("Insufficient funds including credit limit")

        prev_balance = float(self._balance)
        self._balance -= amount
        used_credit = self._balance < 0 or prev_balance < 0
        self._record("withdraw", amount, "success", used_credit=used_credit)

    def _record(self, op_type: str, amount: float, status: str, used_credit: bool | None = None) -> None:
        # Переопределяем, чтобы для кредитного счёта поле used_credit всегда присутствовало (если не задано — False)
        super()._record(op_type, amount, status, used_credit=used_credit if used_credit is not None else False)


__all__ = ["Account", "CreditAccount"]
