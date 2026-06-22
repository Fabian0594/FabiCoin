import time

import pytest

from domain.transaction import Transaction
from domain.wallet import Wallet


def test_transaction_creation() -> None:
    now = time.time()
    sender = "Alice"
    recipient = "Bob"
    amount = 50.0

    tx_id = Transaction.calculate_hash(sender, recipient, amount, now)
    tx = Transaction(
        sender=sender, recipient=recipient, amount=amount, timestamp=now, id=tx_id
    )

    assert tx.sender == "Alice"
    assert tx.recipient == "Bob"
    assert tx.amount == 50.0
    assert tx.timestamp == now
    assert tx.id == tx_id
    assert tx.signature == ""


def test_transaction_hash_deterministic() -> None:
    sender = "Alice"
    recipient = "Bob"
    amount = 10.5
    timestamp = 1600000000.0

    hash1 = Transaction.calculate_hash(sender, recipient, amount, timestamp)
    hash2 = Transaction.calculate_hash(sender, recipient, amount, timestamp)

    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex digest length


def test_transaction_hash_changes_with_different_inputs() -> None:
    sender = "Alice"
    recipient = "Bob"
    amount = 10.5
    timestamp = 1600000000.0

    base_hash = Transaction.calculate_hash(sender, recipient, amount, timestamp)

    # Change sender
    assert base_hash != Transaction.calculate_hash(
        "Charlie", recipient, amount, timestamp
    )

    # Change recipient
    assert base_hash != Transaction.calculate_hash(sender, "Charlie", amount, timestamp)

    # Change amount
    assert base_hash != Transaction.calculate_hash(
        sender, recipient, amount + 1.0, timestamp
    )

    # Change timestamp
    assert base_hash != Transaction.calculate_hash(
        sender, recipient, amount, timestamp + 1.0
    )


def test_transaction_signing_success() -> None:
    wallet = Wallet()
    recipient_wallet = Wallet()
    now = time.time()
    amount = 100.0

    tx_id = Transaction.calculate_hash(
        wallet.public_key, recipient_wallet.public_key, amount, now
    )
    tx = Transaction(
        sender=wallet.public_key,
        recipient=recipient_wallet.public_key,
        amount=amount,
        timestamp=now,
        id=tx_id,
    )

    # Initially unsigned, is_valid raises ValueError
    with pytest.raises(ValueError, match="La transacción no está firmada"):
        tx.is_valid()

    # Sign transaction
    tx.sign_transaction(wallet.private_key)
    assert tx.signature != ""
    assert tx.is_valid() is True


def test_transaction_signing_failure_wrong_private_key() -> None:
    wallet = Wallet()
    attacker_wallet = Wallet()
    recipient_wallet = Wallet()
    now = time.time()
    amount = 50.0

    tx_id = Transaction.calculate_hash(
        wallet.public_key, recipient_wallet.public_key, amount, now
    )
    tx = Transaction(
        sender=wallet.public_key,
        recipient=recipient_wallet.public_key,
        amount=amount,
        timestamp=now,
        id=tx_id,
    )

    # Attacker tries to sign with their own private key
    with pytest.raises(ValueError, match="la clave privada no corresponde al emisor"):
        tx.sign_transaction(attacker_wallet.private_key)


def test_transaction_is_valid_coinbase() -> None:
    recipient_wallet = Wallet()
    now = time.time()
    amount = 10.0

    tx_id = Transaction.calculate_hash(
        "NETWORK", recipient_wallet.public_key, amount, now
    )
    tx = Transaction(
        sender="NETWORK",
        recipient=recipient_wallet.public_key,
        amount=amount,
        timestamp=now,
        id=tx_id,
    )

    # Coinbase transaction (sender="NETWORK") does not need a signature
    assert tx.is_valid() is True


def test_transaction_is_valid_tampered_signature() -> None:
    wallet = Wallet()
    recipient_wallet = Wallet()
    now = time.time()
    amount = 10.0

    tx_id = Transaction.calculate_hash(
        wallet.public_key, recipient_wallet.public_key, amount, now
    )
    tx = Transaction(
        sender=wallet.public_key,
        recipient=recipient_wallet.public_key,
        amount=amount,
        timestamp=now,
        id=tx_id,
    )

    tx.sign_transaction(wallet.private_key)
    assert tx.is_valid() is True

    # Tamper with the signature
    original_sig = tx.signature
    tx.signature = "f" * len(original_sig)
    assert tx.is_valid() is False


def test_transaction_is_valid_tampered_id() -> None:
    wallet = Wallet()
    recipient_wallet = Wallet()
    now = time.time()
    amount = 10.0

    tx_id = Transaction.calculate_hash(
        wallet.public_key, recipient_wallet.public_key, amount, now
    )
    tx = Transaction(
        sender=wallet.public_key,
        recipient=recipient_wallet.public_key,
        amount=amount,
        timestamp=now,
        id=tx_id,
    )

    tx.sign_transaction(wallet.private_key)
    assert tx.is_valid() is True

    # Tamper with the transaction ID/hash
    tx.id = "f" * 64
    assert tx.is_valid() is False
