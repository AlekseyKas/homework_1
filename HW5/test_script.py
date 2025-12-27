"""Pytest unit tests для `script.py`.

Файл `test_solution.py` переименован в `test_script.py` и обновлён
импорт, а также дополнен русскими комментариями внутри тестов.
"""
import pytest
from datetime import datetime

# Импортируем классы из нового файла `script.py`
from script import Account, CreditAccount


def test_account_init_invalid_name():
    # Пустое имя владельца должно приводить к ошибке
    with pytest.raises(ValueError):
        Account('', 0)


def test_account_init_negative_balance():
    # Нельзя инициализировать обычный счёт с отрицательным балансом
    with pytest.raises(ValueError):
        Account('Alice', -1)


def test_deposit_invalid_type_and_negative():
    a = Account('T', 10)
    # Некорректный тип суммы
    with pytest.raises(ValueError):
        a.deposit('not a number')
    # Отрицательное пополнение
    with pytest.raises(ValueError):
        a.deposit(-5)


def test_deposit_success_updates_balance_and_history():
    # Успешный депозит: баланс и история обновляются корректно
    a = Account('Bob', 20)
    a.deposit(30)
    assert a.get_balance() == pytest.approx(50.0)
    hist = a.get_history()
    assert hist[-1]['type'] == 'deposit'
    assert hist[-1]['amount'] == 30.0
    assert hist[-1]['status'] == 'success'


def test_withdraw_insufficient_funds_records_fail():
    # Попытка снятия больше баланса должна быть зафиксирована как 'fail'
    a = Account('C', 10)
    with pytest.raises(ValueError):
        a.withdraw(20)
    hist = a.get_history()
    assert hist[-1]['type'] == 'withdraw'
    assert hist[-1]['status'] == 'fail'


def test_withdraw_success_updates_balance_and_history():
    # Успешное снятие корректно уменьшает баланс и заносит запись
    a = Account('D', 100)
    a.withdraw(40)
    assert a.get_balance() == pytest.approx(60.0)
    last = a.get_history()[-1]
    assert last['type'] == 'withdraw' and last['status'] == 'success'
    # баланс в истории должен совпадать с get_balance() после операции
    assert last['balance'] == pytest.approx(a.get_balance())


def test_history_datetime_isoformat():
    # Проверяем, что поле datetime в истории имеет ISO-формат
    a = Account('E', 5)
    a.deposit(5)
    last = a.get_history()[-1]
    dt = datetime.fromisoformat(last['datetime'])
    assert isinstance(dt, datetime)


def test_history_is_copy_not_reference():
    # get_history() возвращает копию списка, изменение внешней копии не меняет внутренний список
    a = Account('F', 10)
    a.deposit(5)
    h = a.get_history()
    h.append({'type': 'fake'})
    assert len(a.operations_history) != len(h)


def test_creditaccount_initialization_and_limits():
    # Нельзя задать начальный баланс меньше, чем -credit_limit
    with pytest.raises(ValueError):
        CreditAccount('G', balance=-500, credit_limit=400)
    # Инициализация в пределах лимита допустима
    c = CreditAccount('G', balance=-100, credit_limit=200)
    assert c.get_balance() == -100.0
    assert c.get_available_credit() == 100.0


def test_credit_withdraw_and_used_credit_field():
    # Снятие, которое использует кредитные средства, фиксируется с used_credit True
    c = CreditAccount('H', balance=0, credit_limit=300)
    c.withdraw(200)
    assert c.get_balance() == -200.0
    last = c.get_history()[-1]
    assert last['status'] == 'success'
    assert last.get('used_credit', False) is True


def test_credit_withdraw_exceed_limit():
    # Попытка превысить кредитный лимит фиксируется как ошибка и как 'fail' в истории
    c = CreditAccount('I', balance=0, credit_limit=100)
    with pytest.raises(ValueError):
        c.withdraw(201)
    last = c.get_history()[-1]
    assert last['status'] == 'fail'


def test_credit_deposit_clears_used_credit_flag():
    # Пополнение должно корректно обновлять used_credit в истории
    c = CreditAccount('J', balance=0, credit_limit=200)
    c.withdraw(150)
    assert c.get_balance() == -150
    c.deposit(200)
    assert c.get_balance() == pytest.approx(50.0)
    last = c.get_history()[-1]
    assert 'used_credit' in last
    assert last['used_credit'] in (True, False)


def test_non_numeric_withdraw_deposit_credit():
    # Некорректные типы в операциях должны вызывать ValueError
    c = CreditAccount('K', balance=0, credit_limit=100)
    with pytest.raises(ValueError):
        c.withdraw('abc')
    with pytest.raises(ValueError):
        c.deposit('xyz')
