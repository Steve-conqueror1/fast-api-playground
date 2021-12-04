import pytest

from app.calculations import (
    add,
    subtract,
    multiply,
    divide,
    BankAccount,
    InsufficientFunds,
)


@pytest.fixture
def zero_bank_account():
    return BankAccount()


@pytest.fixture
def bank_account():
    return BankAccount(50)


@pytest.mark.parametrize(
    "num1, num2, expected",
    [
        (3, 5, 8),
        (3, 1, 4),
        (3, 45, 48),
        (3, 1005, 1008),
    ],
)
def test_add(num1, num2, expected):
    assert add(num1, num2) == expected


def test_subtract():
    assert subtract(18, 9) == 9


def test_multiply():
    assert multiply(5, 9) == 45


def test_divide():
    assert divide(18, 9) == 2


def test_bank_set_initial_amount(bank_account):
    assert bank_account.balance == 50


def test_bank_set_default_amount(zero_bank_account):
    assert zero_bank_account.balance == 0


def test_withdraw(bank_account):
    bank_account.withdraw(20)
    assert bank_account.balance == 30


def test_deposit(bank_account):
    bank_account.deposit(30)
    assert bank_account.balance == 80


def test_collect_interest(bank_account):
    bank_account.collect_interests()
    assert bank_account.balance == 75


@pytest.mark.parametrize(
    "deposited, withdraw, expected",
    [
        (200, 100, 100),
        (23, 1, 22),
        (90, 45, 45),
    ],
)
def test_bank_transactions(zero_bank_account, deposited, withdraw, expected):
    zero_bank_account.deposit(deposited)
    zero_bank_account.withdraw(withdraw)
    assert zero_bank_account.balance == expected


def test_insufficient_funds(bank_account):
    with pytest.raises(InsufficientFunds):
        bank_account.withdraw(200)
