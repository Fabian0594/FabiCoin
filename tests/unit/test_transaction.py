import time

from domain.transaction import Transaction


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
