import hashlib

from domain.merkle_tree import build_merkle_root
from domain.transaction import Transaction


def test_build_merkle_root_empty() -> None:
    # An empty transaction list should return the hash of an empty string
    expected = hashlib.sha256(b"").hexdigest()
    assert build_merkle_root([]) == expected


def test_build_merkle_root_single() -> None:
    tx = Transaction(
        sender="sender_address",
        recipient="recipient_address",
        amount=10.0,
        timestamp=1600000000.0,
        id="tx_id_1",
    )
    # A single transaction should return its own ID as the root
    assert build_merkle_root([tx]) == "tx_id_1"


def test_build_merkle_root_even_two() -> None:
    tx1 = Transaction(
        sender="sender", recipient="recipient", amount=5.0, timestamp=1.0, id="id1"
    )
    tx2 = Transaction(
        sender="sender", recipient="recipient", amount=10.0, timestamp=2.0, id="id2"
    )

    expected = hashlib.sha256(b"id1id2").hexdigest()
    assert build_merkle_root([tx1, tx2]) == expected


def test_build_merkle_root_odd_three() -> None:
    tx1 = Transaction(sender="s", recipient="r", amount=1.0, timestamp=1.0, id="id1")
    tx2 = Transaction(sender="s", recipient="r", amount=2.0, timestamp=2.0, id="id2")
    tx3 = Transaction(sender="s", recipient="r", amount=3.0, timestamp=3.0, id="id3")

    # First level:
    # pair 1: id1 + id2 -> hash12
    # pair 2: id3 + id3 (duplicated) -> hash33
    hash12 = hashlib.sha256(b"id1id2").hexdigest()
    hash33 = hashlib.sha256(b"id3id3").hexdigest()

    # Second level:
    # pair: hash12 + hash33 -> root
    expected = hashlib.sha256((hash12 + hash33).encode("utf-8")).hexdigest()
    assert build_merkle_root([tx1, tx2, tx3]) == expected
