"""Простой тестовый раннер для решения HW5.

Запуск:
  `python3 run_tests.py` из директории `HW5` или
  `python3 HW5/run_tests.py` из корня репозитория.
"""
from script import Account, CreditAccount


def main() -> None:
    # Проверка инициализации Account
    try:
        Account("", 0)
        raise AssertionError("Empty account_holder should raise ValueError")
    except ValueError:
        pass

    try:
        Account("Alice", -10)
        raise AssertionError("Negative initial balance should raise ValueError")
    except ValueError:
        pass

    a = Account("Alice", 100)
    assert a.get_balance() == 100.0

    # Некорректный депозит
    try:
        a.deposit(-5)
        raise AssertionError("Negative deposit must raise")
    except ValueError:
        pass

    # Успешный депозит
    a.deposit(50)
    assert a.get_balance() == 150.0
    hist = a.get_history()
    assert isinstance(hist, list) and hist, "History should be non-empty list"
    last = hist[-1]
    assert last["type"] == "deposit"
    assert last["amount"] == 50.0
    assert last["status"] == "success"
    assert "datetime" in last

    # Попытка снять больше, чем баланс
    try:
        a.withdraw(200)
        raise AssertionError("Withdraw more than balance should raise")
    except ValueError:
        pass

    # Успешное снятие
    a.withdraw(25)
    assert a.get_balance() == 125.0
    last = a.get_history()[-1]
    assert last["type"] == "withdraw" and last["status"] == "success"

    # Тесты для CreditAccount
    try:
        CreditAccount("Bob", balance=-500, credit_limit=400)
        raise AssertionError("Initial balance below -credit_limit should raise")
    except ValueError:
        pass

    c = CreditAccount("Bob", balance=0, credit_limit=300)
    assert c.get_available_credit() == 300.0

    # Снятие в пределах кредитного лимита
    c.withdraw(200)
    assert c.get_balance() == -200.0
    last = c.get_history()[-1]
    assert last["status"] == "success"
    assert last.get("used_credit", False) is True
    assert c.get_available_credit() == 100.0

    # Попытка превысить кредитный лимит
    try:
        c.withdraw(500)
        raise AssertionError("Withdraw beyond credit limit should raise")
    except ValueError:
        pass

    # Пополнение для восстановления положительного баланса
    c.deposit(250)
    assert c.get_balance() == 50.0
    last = c.get_history()[-1]
    # Пополнение в кредитном счёте также содержит поле used_credit (False после восстановления)
    assert "used_credit" in last

    print("All tests passed")


if __name__ == "__main__":
    main()
