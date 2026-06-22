import time

from domain.block import Block
from domain.blockchain import Blockchain
from domain.transaction import Transaction


def test_blockchain_initialization_creates_genesis_block() -> None:
    blockchain = Blockchain()

    assert len(blockchain.chain) == 1
    genesis = blockchain.chain[0]
    assert genesis.index == 0
    assert genesis.transactions == []
    assert genesis.previous_hash == "0"
    assert genesis.nonce == 0
    # The hash should be valid and recalculatable
    expected_hash = Block.calculate_hash(
        genesis.index,
        genesis.timestamp,
        genesis.transactions,
        genesis.previous_hash,
        genesis.nonce,
    )
    assert genesis.hash == expected_hash


def test_get_latest_block() -> None:
    blockchain = Blockchain()
    latest = blockchain.get_latest_block()

    assert latest == blockchain.chain[0]  # Initially it's the genesis block


def test_add_block() -> None:
    blockchain = Blockchain()
    genesis = blockchain.get_latest_block()

    new_timestamp = time.time()
    tx = Transaction("Alice", "Bob", 5.0, new_timestamp, "tx_id")
    transactions = [tx]
    new_index = 1
    new_nonce = 42

    # Calculate valid hash
    new_hash = Block.calculate_hash(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=genesis.hash,
        nonce=new_nonce,
    )

    new_block = Block(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=genesis.hash,
        nonce=new_nonce,
        hash=new_hash,
    )

    blockchain.add_block(new_block)

    assert len(blockchain.chain) == 2
    assert blockchain.get_latest_block() == new_block
    assert blockchain.chain[1] == new_block


def test_add_block_invalid_previous_hash() -> None:
    import pytest

    blockchain = Blockchain()
    new_timestamp = time.time()
    tx = Transaction("Alice", "Bob", 5.0, new_timestamp, "tx_id")
    transactions = [tx]
    new_index = 1
    new_nonce = 42

    # Wrong previous hash
    wrong_previous_hash = "wrong_hash"
    new_hash = Block.calculate_hash(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=wrong_previous_hash,
        nonce=new_nonce,
    )

    new_block = Block(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=wrong_previous_hash,
        nonce=new_nonce,
        hash=new_hash,
    )

    with pytest.raises(ValueError, match="Bloque inválido: previous_hash incorrecto"):
        blockchain.add_block(new_block)


def test_add_block_invalid_hash() -> None:
    import pytest

    blockchain = Blockchain()
    genesis = blockchain.get_latest_block()
    new_timestamp = time.time()
    tx = Transaction("Alice", "Bob", 5.0, new_timestamp, "tx_id")
    transactions = [tx]
    new_index = 1
    new_nonce = 42

    # Wrong block hash
    wrong_hash = "wrong_hash"
    new_block = Block(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=genesis.hash,
        nonce=new_nonce,
        hash=wrong_hash,
    )

    with pytest.raises(ValueError, match="Bloque inválido: hash incorrecto"):
        blockchain.add_block(new_block)


def test_blockchain_newly_created_is_valid() -> None:
    blockchain = Blockchain()
    assert blockchain.is_chain_valid() is True


def test_blockchain_immutability_tampered_data() -> None:
    blockchain = Blockchain()
    genesis = blockchain.get_latest_block()

    new_timestamp = time.time()
    tx = Transaction("Alice", "Bob", 10.0, new_timestamp, "tx_id_orig")
    transactions = [tx]
    new_index = 1
    new_nonce = 100
    new_hash = Block.calculate_hash(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=genesis.hash,
        nonce=new_nonce,
    )
    new_block = Block(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=genesis.hash,
        nonce=new_nonce,
        hash=new_hash,
    )
    blockchain.add_block(new_block)

    assert blockchain.is_chain_valid() is True

    # Tamper with the block transactions (changing the list)
    tampered_tx = Transaction("Alice", "Bob", 999.0, new_timestamp, "tx_id_tampered")
    new_block.transactions = [tampered_tx]

    assert blockchain.is_chain_valid() is False


def test_blockchain_immutability_tampered_previous_hash() -> None:
    blockchain = Blockchain()
    genesis = blockchain.get_latest_block()

    new_timestamp = time.time()
    tx = Transaction("Alice", "Bob", 10.0, new_timestamp, "tx_id")
    transactions = [tx]
    new_index = 1
    new_nonce = 100
    new_hash = Block.calculate_hash(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=genesis.hash,
        nonce=new_nonce,
    )
    new_block = Block(
        index=new_index,
        timestamp=new_timestamp,
        transactions=transactions,
        previous_hash=genesis.hash,
        nonce=new_nonce,
        hash=new_hash,
    )
    blockchain.add_block(new_block)

    assert blockchain.is_chain_valid() is True

    # Tamper with previous_hash and update current hash to satisfy Invariant 1
    new_block.previous_hash = "wrong_previous_hash"
    new_block.hash = Block.calculate_hash(
        new_block.index,
        new_block.timestamp,
        new_block.transactions,
        new_block.previous_hash,
        new_block.nonce,
    )

    assert blockchain.is_chain_valid() is False
