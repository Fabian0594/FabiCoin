import time

from domain.block import Block
from domain.blockchain import Blockchain


def test_blockchain_initialization_creates_genesis_block() -> None:
    blockchain = Blockchain()

    assert len(blockchain.chain) == 1
    genesis = blockchain.chain[0]
    assert genesis.index == 0
    assert genesis.data == "Genesis Block"
    assert genesis.previous_hash == "0"
    assert genesis.nonce == 0
    # The hash should be valid and recalculatable
    expected_hash = Block.calculate_hash(
        genesis.index,
        genesis.timestamp,
        genesis.data,
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
    new_data = "Transaction: Alice pays Bob 5 Coins"
    new_index = 1
    new_nonce = 42

    # Calculate valid hash
    new_hash = Block.calculate_hash(
        index=new_index,
        timestamp=new_timestamp,
        data=new_data,
        previous_hash=genesis.hash,
        nonce=new_nonce,
    )

    new_block = Block(
        index=new_index,
        timestamp=new_timestamp,
        data=new_data,
        previous_hash=genesis.hash,
        nonce=new_nonce,
        hash=new_hash,
    )

    blockchain.add_block(new_block)

    assert len(blockchain.chain) == 2
    assert blockchain.get_latest_block() == new_block
    assert blockchain.chain[1] == new_block


def test_blockchain_newly_created_is_valid() -> None:
    blockchain = Blockchain()
    assert blockchain.is_chain_valid() is True


def test_blockchain_immutability_tampered_data() -> None:
    blockchain = Blockchain()
    genesis = blockchain.get_latest_block()

    new_timestamp = time.time()
    new_data = "Original Transaction"
    new_index = 1
    new_nonce = 100
    new_hash = Block.calculate_hash(
        index=new_index,
        timestamp=new_timestamp,
        data=new_data,
        previous_hash=genesis.hash,
        nonce=new_nonce,
    )
    new_block = Block(
        index=new_index,
        timestamp=new_timestamp,
        data=new_data,
        previous_hash=genesis.hash,
        nonce=new_nonce,
        hash=new_hash,
    )
    blockchain.add_block(new_block)

    assert blockchain.is_chain_valid() is True

    # Tamper with the block data
    new_block.data = "Tampered Transaction"

    assert blockchain.is_chain_valid() is False


def test_blockchain_immutability_tampered_previous_hash() -> None:
    blockchain = Blockchain()
    genesis = blockchain.get_latest_block()

    new_timestamp = time.time()
    new_data = "Transaction"
    new_index = 1
    new_nonce = 100
    new_hash = Block.calculate_hash(
        index=new_index,
        timestamp=new_timestamp,
        data=new_data,
        previous_hash=genesis.hash,
        nonce=new_nonce,
    )
    new_block = Block(
        index=new_index,
        timestamp=new_timestamp,
        data=new_data,
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
        new_block.data,
        new_block.previous_hash,
        new_block.nonce,
    )

    assert blockchain.is_chain_valid() is False
