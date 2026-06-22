import pytest

from domain.wallet import InsufficientFundsError, Wallet


def test_wallet_initial_balance() -> None:
    wallet = Wallet(100.0)
    assert wallet.balance == 100.0


def test_wallet_default_balance() -> None:
    wallet = Wallet()
    assert wallet.balance == 0.0


def test_wallet_negative_initial_balance() -> None:
    with pytest.raises(ValueError, match="Initial balance cannot be negative"):
        Wallet(-10.0)


def test_wallet_deposit() -> None:
    wallet = Wallet(50.0)
    wallet.deposit(25.0)
    assert wallet.balance == 75.0


def test_wallet_deposit_invalid_amount() -> None:
    wallet = Wallet(50.0)
    with pytest.raises(ValueError, match="Deposit amount must be positive"):
        wallet.deposit(-5.0)


def test_wallet_withdraw() -> None:
    wallet = Wallet(100.0)
    wallet.withdraw(40.0)
    assert wallet.balance == 60.0


def test_wallet_withdraw_insufficient_funds() -> None:
    wallet = Wallet(20.0)
    with pytest.raises(InsufficientFundsError, match="Insufficient funds"):
        wallet.withdraw(30.0)


def test_wallet_withdraw_invalid_amount() -> None:
    wallet = Wallet(50.0)
    with pytest.raises(ValueError, match="Withdrawal amount must be positive"):
        wallet.withdraw(-10.0)
