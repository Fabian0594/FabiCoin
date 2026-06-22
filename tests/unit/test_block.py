import time

from domain.block import Block
from domain.transaction import Transaction


def test_block_creation() -> None:
    now = time.time()
    tx = Transaction("Alice", "Bob", 10.0, now, "tx_id")
    block = Block(
        index=0,
        timestamp=now,
        transactions=[tx],
        previous_hash="0",
        nonce=100,
        hash="genesis_hash",
    )

    assert block.index == 0
    assert block.timestamp == now
    assert block.transactions == [tx]
    assert block.previous_hash == "0"
    assert block.nonce == 100
    assert block.hash == "genesis_hash"


def test_block_equality() -> None:
    now = time.time()
    tx = Transaction("Alice", "Bob", 10.0, now, "tx_id")
    block1 = Block(
        index=1,
        timestamp=now,
        transactions=[tx],
        previous_hash="genesis_hash",
        nonce=200,
        hash="block_hash",
    )
    block2 = Block(
        index=1,
        timestamp=now,
        transactions=[tx],
        previous_hash="genesis_hash",
        nonce=200,
        hash="block_hash",
    )

    assert block1 == block2


def test_block_hash_deterministic() -> None:
    index = 1
    timestamp = 1600000000.0
    tx = Transaction("Alice", "Bob", 10.0, timestamp, "tx_id")
    transactions = [tx]
    previous_hash = "genesis_hash"
    nonce = 42

    hash1 = Block.calculate_hash(index, timestamp, transactions, previous_hash, nonce)
    hash2 = Block.calculate_hash(index, timestamp, transactions, previous_hash, nonce)

    # El hash debe ser determinista (misma entrada produce mismo hash)
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex digest length


def test_block_hash_changes_with_different_inputs() -> None:
    index = 1
    timestamp = 1600000000.0
    tx = Transaction("Alice", "Bob", 10.0, timestamp, "tx_id")
    transactions = [tx]
    previous_hash = "genesis_hash"
    nonce = 42

    base_hash = Block.calculate_hash(
        index, timestamp, transactions, previous_hash, nonce
    )

    # Modificar index
    assert base_hash != Block.calculate_hash(
        index + 1, timestamp, transactions, previous_hash, nonce
    )

    # Modificar timestamp
    assert base_hash != Block.calculate_hash(
        index, timestamp + 1.0, transactions, previous_hash, nonce
    )

    # Modificar transactions
    different_tx = Transaction("Alice", "Bob", 20.0, timestamp, "tx_id_different")
    assert base_hash != Block.calculate_hash(
        index, timestamp, [different_tx], previous_hash, nonce
    )

    # Modificar previous_hash
    assert base_hash != Block.calculate_hash(
        index, timestamp, transactions, "new_previous_hash", nonce
    )

    # Modificar nonce
    assert base_hash != Block.calculate_hash(
        index, timestamp, transactions, previous_hash, nonce + 1
    )


def test_block_mining() -> None:
    tx = Transaction("Alice", "Bob", 10.0, 1600000000.0, "tx_id")
    block = Block(
        index=1,
        timestamp=1600000000.0,
        transactions=[tx],
        previous_hash="genesis_hash",
        nonce=0,
        hash="",
    )
    block.mine(2)
    assert block.hash.startswith("00")
    # Verificar que el hash asignado coincide con el recalculado
    expected_hash = Block.calculate_hash(
        block.index,
        block.timestamp,
        block.transactions,
        block.previous_hash,
        block.nonce,
    )
    assert block.hash == expected_hash
